"use client";

import { useState } from "react";

export default function Home() {

  // STATES
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  // INTERNAL INTENT
  const [intent, setIntent] = useState("");

  // HISTORY
  const [history, setHistory] = useState<any[]>([]);

  // MAIN EXECUTION
  const runDynexa = async () => {

    if (!prompt.trim()) return;

    setLoading(true);

    try {

      const res = await fetch("http://127.0.0.1:8000/optimize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: prompt,
        }),
      });

      const data = await res.json();

      setResponse(data.response);

      // Hidden intent tracking
      setIntent(data.intent);

      // SAVE HISTORY
      setHistory((prev) => [
        {
          prompt: prompt,
          response: data.response,
          intent: data.intent,
        },
        ...prev,
      ]);

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

      {/* LOADING */}
      {loading && (

        <div className="mt-10 text-gray-400 animate-pulse text-lg">
          Dynexa intelligence engine processing...
        </div>

      )}

      {/* RESPONSE */}
      {response && !loading && (

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
            shadow-2xl
          "
        >

          <h2 className="text-4xl font-bold">
            Dynexa Response
          </h2>

          {/* HIDDEN INTENT */}
          {intent && (
            <div className="hidden">
              {intent}
            </div>
          )}

          {/* RESPONSE TEXT */}
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

          {/* ACTIONS */}
          <div className="flex gap-4 mt-10">

            {/* COPY */}
            <button
              onClick={() => navigator.clipboard.writeText(response)}

              className="
                bg-white
                text-black
                px-6
                py-3
                rounded-xl
                font-semibold
                hover:scale-105
                transition
              "
            >
              Copy
            </button>

            {/* CLEAR */}
            <button
              onClick={() => {
                setPrompt("");
                setResponse("");
              }}

              className="
                border
                border-zinc-600
                px-6
                py-3
                rounded-xl
                font-semibold
                hover:bg-zinc-800
                transition
              "
            >
              Clear
            </button>

          </div>

        </div>
      )}

      {/* HISTORY */}
      {history.length > 0 && (

        <div className="w-full max-w-5xl mt-20">

          <h2 className="text-3xl font-bold mb-8">
            Recent Sessions
          </h2>

          <div className="space-y-6">

            {history.map((item, index) => (

              <div
                key={index}

                className="
                  bg-zinc-900
                  border
                  border-zinc-700
                  rounded-2xl
                  p-7
                "
              >

                {/* USER */}
                <div className="text-gray-400">

                  <span className="font-semibold text-white">
                    Input:
                  </span>

                  <div className="mt-3">
                    {item.prompt}
                  </div>

                </div>

                {/* RESPONSE */}
                <div className="mt-8 text-gray-300">

                  <span className="font-semibold text-white">
                    Response:
                  </span>

                  <div className="mt-3 whitespace-pre-wrap">
                    {item.response}
                  </div>

                </div>

              </div>

            ))}

          </div>

        </div>
      )}

    </main>
  );
}