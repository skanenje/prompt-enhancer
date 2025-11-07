async function loadFrameworks() {
  const select = document.getElementById("frameworkSelect");
  select.innerHTML = "<option>Loading...</option>";

  try {
    const res = await fetch("http://127.0.0.1:8000/frameworks");
    const data = await res.json();

    select.innerHTML = "";
    data.frameworks.forEach(fw => {
      const opt = document.createElement("option");
      opt.value = fw.id;
      opt.textContent = `${fw.name} - ${fw.description}`;
      select.appendChild(opt);
    });

  } catch (err) {
    select.innerHTML = "<option>Error loading frameworks</option>";
    console.error("Framework load failed:", err);
  }
}

document.addEventListener("DOMContentLoaded", loadFrameworks);
