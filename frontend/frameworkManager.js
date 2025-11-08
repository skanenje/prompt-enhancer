async function loadFrameworks() {
  const select = document.getElementById("frameworkSelect");
  const enhanceBtn = document.getElementById("enhanceBtn");
  
  select.innerHTML = "<option>Loading...</option>";
  enhanceBtn.disabled = true;

  try {
    const res = await fetch("api/frameworks");
    const data = await res.json();

    select.innerHTML = "<option value=''>Choose a framework...</option>";
    data.frameworks.forEach(fw => {
      const opt = document.createElement("option");
      opt.value = fw.id;
      opt.textContent = `${fw.name} - ${fw.description}`;
      select.appendChild(opt);
    });
    
    enhanceBtn.disabled = false;

  } catch (err) {
    select.innerHTML = "<option>Error loading frameworks</option>";
    console.error("Framework load failed:", err);
  }
}

document.addEventListener("DOMContentLoaded", loadFrameworks);
