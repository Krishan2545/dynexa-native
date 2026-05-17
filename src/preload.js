window.addEventListener("DOMContentLoaded", () => {

    const button = document.getElementById("optimizeBtn");
  
    button.addEventListener("click", async () => {
  
      const prompt = document.getElementById("prompt").value;
  
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
        <h3>Optimized Result</h3>
  
        <p><b>Prompt:</b> ${data.optimized_prompt}</p>
  
        <p><b>Provider:</b> ${data.provider_selected}</p>
  
        <p><b>Cost Saved:</b> ${data.estimated_cost_saved}</p>
      `;
    });
  
  });