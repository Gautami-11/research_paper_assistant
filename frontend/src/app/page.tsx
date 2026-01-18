"use client";
import { useState, useEffect } from "react";
import axios from "axios";

export default function Home() {
  const [sessionId, setSessionId] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  // 1️⃣ Generate/Retrieve Unique Session ID
  useEffect(() => {
    let id = localStorage.getItem("chat_session_id");
    if (!id) {
        id = crypto.randomUUID(); 
        localStorage.setItem("chat_session_id", id);
    }
    setSessionId(id);
  }, []);

  const uploadPDF = async () => {
    if (!file) return alert("Please select a file first");

    const formData = new FormData();
    formData.append("file", file);
    // ✅ Send Session ID
    formData.append("session_id", sessionId); 

    try {
      setLoading(true);
      await axios.post("http://127.0.0.1:8000/upload", formData);
      alert("PDF Uploaded Successfully!");
    } catch (error) {
      console.error(error);
      alert("Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const askQuestion = async () => {
    if (!question) return;

    try {
      setLoading(true);
      const response = await axios.post(
        "http://127.0.0.1:8000/ask",
        null,
        {
          params: { query: question },
          // ✅ Send Session ID in Headers
          headers: { "session-id": sessionId } 
        }
      );
      setAnswer(response.data.answer);
    } catch (error) {
      console.error(error);
      setAnswer("Error getting answer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-10 px-4">
      <div className="w-full max-w-2xl bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-8 flex items-center gap-2 border-b pb-4">
          📄 Research Paper Q&A <span className="text-xs font-normal text-gray-400 mt-2">ID: {sessionId.slice(0,6)}</span>
        </h1>

        {/* Upload Section */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">1️⃣ Upload PDF</h3>
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
            <input
              type="file"
              accept="application/pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="block w-full text-sm text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
            />
            <button
              onClick={uploadPDF}
              disabled={loading || !sessionId}
              className="bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-6 rounded-lg transition-colors shadow-sm whitespace-nowrap disabled:opacity-50"
            >
              {loading ? "Uploading..." : "Upload"}
            </button>
          </div>
        </div>

        {/* Question Section */}
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">2️⃣ Ask a Question</h3>
          <div className="flex flex-col gap-4">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="What is the methodology used?"
              className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              onClick={askQuestion}
              disabled={loading || !sessionId}
              className="bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2.5 px-6 rounded-lg disabled:opacity-50"
            >
              {loading ? "Asking..." : "Ask Question"}
            </button>
          </div>
        </div>

        {/* Answer Section */}
        <div className="mt-8 pt-6 border-t border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-3">Answer</h3>
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-5 ">
            {answer ? (
              <pre className="whitespace-pre-wrap font-mono text-sm text-slate-700 leading-relaxed">
                {answer}
              </pre>
            ) : (
              <p className="text-slate-400 italic text-sm">
                The AI response will appear here...
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}