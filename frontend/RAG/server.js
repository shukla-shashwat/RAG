// server.js (Gemini backend with PDF/TXT saving)

require("dotenv").config();
const MODEL_ID = "models/gemini-2.5-flash"; // from your /models list

const express = require("express");
const cors = require("cors");
const multer = require("multer");
const fs = require("fs");
const path = require("path");

// Proper fetch polyfill for CommonJS + node-fetch v3
const fetch = (...args) =>
  import("node-fetch").then(({ default: fetch }) => fetch(...args));

const app = express();

/* ---------- FILE STORAGE SETUP (PDF / TEXT ONLY) ---------- */

// Base upload directories
const baseUploadDir = path.join(__dirname, "uploads");
const pdfDir = path.join(baseUploadDir, "pdf");
const textDir = path.join(baseUploadDir, "text");
const uploadsLogPath = path.join(baseUploadDir, "uploads-log.json");

// Ensure folders exist
[baseUploadDir, pdfDir, textDir].forEach((dir) => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
});

// Multer storage: choose folder based on MIME type
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const mime = file.mimetype;

    if (mime === "application/pdf") {
      cb(null, pdfDir);
    } else if (mime === "text/plain") {
      cb(null, textDir);
    } else {
      // Fallback (should be filtered out by fileFilter)
      cb(null, baseUploadDir);
    }
  },
  filename: (req, file, cb) => {
    const timestamp = Date.now();
    const safeName = file.originalname.replace(/\s+/g, "_");
    cb(null, `${timestamp}_${safeName}`);
  },
});

// Only allow PDFs and plain text
const fileFilter = (req, file, cb) => {
  const mime = file.mimetype;
  if (mime === "application/pdf" || mime === "text/plain") {
    cb(null, true); // accept
  } else {
    console.warn(
      `Rejected file type: ${file.originalname} (${file.mimetype}). Only PDF and text allowed.`
    );
    cb(null, false); // reject silently
  }
};

const upload = multer({ storage, fileFilter });

// Log info about saved files into uploads/uploads-log.json
function saveFileRecord(file) {
  if (!file) return;

  const record = {
    originalName: file.originalname,
    storedName: file.filename,
    path: file.path,
    mimetype: file.mimetype,
    size: file.size,
    uploadedAt: new Date().toISOString(),
  };

  let existing = [];
  if (fs.existsSync(uploadsLogPath)) {
    try {
      existing = JSON.parse(fs.readFileSync(uploadsLogPath, "utf8"));
    } catch {
      existing = [];
    }
  }

  existing.push(record);
  fs.writeFileSync(uploadsLogPath, JSON.stringify(existing, null, 2), "utf8");
}

/* ---------- APP / CORS / JSON ---------- */

// allow your React app on port 5001
app.use(
  cors({
    origin: "http://localhost:5001",
  })
);

app.use(express.json());

// Test route
app.get("/", (req, res) => {
  res.send("Backend API is running with Gemini ✨");
});

/* ---------- MAIN CHAT ENDPOINT ---------- */

app.post("/api/chat", upload.single("file"), async (req, res) => {
  try {
    const userMessage = req.body.message || "";
    const uploadedFile = req.file || null;

    console.log("Message:", userMessage);

    // If there is a valid file (pdf or txt) it is already saved by multer.
    if (uploadedFile) {
      console.log("File saved:", uploadedFile.path);
      saveFileRecord(uploadedFile);
    } else if (req.file === undefined && req.body && !userMessage.trim()) {
      // No valid file and no text – tell user
      return res.json({
        reply:
          "Only PDF (.pdf) or plain text (.txt) files are supported, and you didn't send any text message.",
      });
    }

    const geminiKey = process.env.GEMINI_API_KEY;
    if (!geminiKey) {
      return res
        .status(500)
        .json({ reply: "Gemini API Key missing ❌ (set GEMINI_API_KEY in .env)" });
    }

    // Build prompt: include note if a file was uploaded
    let fullUserText = userMessage || "";
    if (uploadedFile) {
      fullUserText += `\n\n[The user also uploaded a file named "${uploadedFile.originalname}" stored at "${uploadedFile.path}".]`;
    }

    const response = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/${MODEL_ID}:generateContent?key=${geminiKey}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          contents: [
            {
              parts: [{ text: fullUserText || "User uploaded a file." }],
            },
          ],
        }),
      }
    );

    const result = await response.json();
    console.log("Gemini Response:", result);

    const text =
      result?.candidates?.[0]?.content?.parts?.[0]?.text ||
      (result?.error?.message
        ? `Gemini error: ${result.error.message}`
        : "No response from Gemini API ⚠️");

    res.json({ reply: text });
  } catch (error) {
    console.error("Server error:", error);
    res
      .status(500)
      .json({ reply: "Server crashed while calling Gemini ❌" });
  }
});

/* ---------- START SERVER ---------- */

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`✅ Gemini Backend running on http://localhost:${PORT}`);
  console.log(`📂 Uploads folder: ${baseUploadDir}`);
});
