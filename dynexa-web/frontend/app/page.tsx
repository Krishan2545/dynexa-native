"use client";

import { useState } from "react";

export default function Home() {

  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  // MAIN EXECUTION
  const runDynexa = async () => {

    if (!prompt.trim()) return;

    setLoading(true);

    setResponse("");

    try {

      const res = await fetch(
        "http://127.0.0.1:8000/optimize",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            prompt: prompt,
          }),
        }
      );

      const reader = res.body?.getReader();

      const decoder = new TextDecoder();

      if (!reader) return;

      while (true) {

        const { done, value } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value);

        setResponse((prev) => prev + chunk);
      }

    } catch (error) {

      console.error(error);

      setResponse("Dynexa backend connection failed.");
    }

    setLoading(false);
  };

  return (

    <main className="min-h-screen bg-black text-white flex flex-col items-center p-10">

      {/* HEADER */}
      <div className="text-center mt-10">

        <h1 className="text-7xl font-bold tracking-tight">
          Dynexa Native
        </h1>

        <p className="text-gray-400 mt-5 text-xl">
          AI Native Intelligence Layer
        </p>

      </div>

      {/* INPUT */}
      <div className="w-full max-w-5xl mt-14">

        <textarea
          value={prompt}

          onChange={(e) => setPrompt(e.target.value)}

          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              runDynexa();
            }
          }}

          placeholder="Ask Dynexa anything..."

          className="
            w-full
            h-72
            p-7
            rounded-3xl
            bg-zinc-900
            border
            border-zinc-700
            text-xl
            outline-none
            resize-none
            focus:border-white
            transition
          "
        />

        {/* BUTTON */}
        <div className="flex justify-center">

          <button
            onClick={runDynexa}

            className="
              mt-8
              px-12
              py-4
              bg-white
              text-black
              rounded-2xl
              text-xl
              font-semibold
              hover:scale-105
              transition
            "
          >
            {loading ? "Thinking..." : "Run Dynexa"}
          </button>

        </div>

      </div>

      {/* RESPONSE */}
      {response && (

        <div
          className="
            w-full
            max-w-5xl
            mt-14
            bg-zinc-900
            border
            border-zinc-700
            rounded-3xl
            p-10
          "
        >

          <h2 className="text-4xl font-bold">
            Dynexa Response
          </h2>

          <div
            className="
              mt-8
              text-gray-300
              text-xl
              leading-10
              whitespace-pre-wrap
            "
          >
            {response}
          </div>

        </div>
      )}

    </main>
  );
}