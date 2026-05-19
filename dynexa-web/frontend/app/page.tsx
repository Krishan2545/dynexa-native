"use client";

import { useState } from "react";

export default function Home() {

  const [prompt, setPrompt] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const optimizePrompt = async () => {

    setLoading(true);
    setResult("");

    try {

      const response = await fetch("http://127.0.0.1:5000/optimize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt,
        }),
      });

      const data = await response.json();

      setResult(data.optimized_prompt);

    } catch (error) {

      setResult("Error connecting backend");

    }

    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-black text-white flex flex-col items-center justify-center p-10">

      <h1 className="text-5xl font-bold mb-6">
        Dynexa Native
      </h1>

      <p className="text-gray-400 mb-10 text-center max-w-xl">
        AI Native Prompt Optimization Layer
      </p>

      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your prompt..."
        className="w-full max-w-2xl h-40 bg-zinc-900 border border-zinc-700 rounded-xl p-4 mb-6"
      />

      <button
        onClick={optimizePrompt}
        className="bg-white text-black px-6 py-3 rounded-xl font-semibold hover:scale-105 transition"
      >
        Optimize Prompt
      </button>

      {loading && (
        <p className="mt-6 text-gray-400">
          Thinking...
        </p>
      )}

      {result && (
        <div className="mt-8 max-w-2xl bg-zinc-900 border border-zinc-700 rounded-xl p-6">
          <h2 className="text-xl font-bold mb-4">
            Optimized Prompt
          </h2>

          <p className="text-gray-300 whitespace-pre-wrap">
            {result}
          </p>
        </div>
      )}

    </main>
  );
}