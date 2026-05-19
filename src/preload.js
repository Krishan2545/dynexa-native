const optimizeBtn = document.getElementById("optimizeBtn");

optimizeBtn.addEventListener("click", async () => {
  const prompt = document.getElementById("prompt").value;

  document.getElementById("result").innerHTML = "Thinking...";

  try {
    const response = await fetch("http://127.0.0.1:5000/optimize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        prompt: prompt
      })
    });

    const data = await response.json();

    document.getElementById("result").innerHTML = `
      <h3>AI Response</h3>
      <p>${data.optimized_prompt}</p>
    `;

  } catch (error) {
    document.getElementById("result").innerHTML = `
      <p style="color:red;">
        Error connecting to backend
      </p>
    `;
  }
});