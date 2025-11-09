const enhanceBtn = document.getElementById("enhanceBtn");
const promptInput = document.getElementById("promptInput");
const frameworkSelect = document.getElementById("frameworkSelect");

const enhancedOutput = document.getElementById("enhancedOutput");
const selectedFramework = document.getElementById("selectedFramework");
const promptScore = document.getElementById("promptScore");
const copyBtn = document.getElementById("copyBtn");

enhanceBtn.addEventListener("click", async () => {
  const prompt = promptInput.value.trim();
  const framework = frameworkSelect.value;

  if (!prompt) {
    alert("Please enter a prompt.");
    return;
  }
  
  if (!framework || framework === "Loading..." || framework === "Error loading frameworks") {
    alert("Please wait for frameworks to load and select one.");
    return;
  }

  enhanceBtn.disabled = true;
  enhanceBtn.textContent = "Enhancing...";

  try {
    const res = await fetch("api/enhance", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, framework_id: framework })
    });

    const data = await res.json();
    
    if (!res.ok || !data.enhanced_prompt) {
      throw new Error(data.detail || 'Invalid response from server');
    }

    enhancedOutput.innerHTML = data.enhanced_prompt.replace(/\n/g, '<br>');
    selectedFramework.textContent = `Framework: ${data.selected_framework}`;
    
    const quality = data.quality;
    promptScore.innerHTML = `
      <div class="quality-metrics">
        <div class="metric">Overall: ${quality.overall}/10</div>
        <div class="metric">Clarity: ${quality.clarity}/10</div>
        <div class="metric">Specificity: ${quality.specificity}/10</div>
        <div class="metric">Context: ${quality.context_richness}/10</div>
        <div class="metric">Actionability: ${quality.actionability}/10</div>
      </div>
    `;

    document.getElementById("output-card").classList.remove("hidden");
  } catch (err) {
    console.error("Enhancement failed:", err);
    alert("Something went wrong.");
  } finally {
    enhanceBtn.disabled = false;
    enhanceBtn.textContent = "Enhance Prompt";
  }
});

copyBtn.addEventListener("click", () => {
  navigator.clipboard.writeText(enhancedOutput.textContent);
  copyBtn.textContent = "Copied!";
  setTimeout(() => (copyBtn.textContent = "Copy to Clipboard"), 1500);
});
