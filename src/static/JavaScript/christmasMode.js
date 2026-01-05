const html = document.documentElement;
const toggleBtn = document.getElementById("themeToggle")

// Load theme from localStorage on page load 
const savedTheme = localStorage.getItem("theme");

if (savedTheme) {
    html.setAttribute("data-theme", savedTheme);
}

// Toggle theme on click 
toggleBtn.addEventListener("click", () => {
    const current = html.getAttribute("data-theme");
    const newTheme = current === "christmas" ? "default" : "christmas"

    html.setAttribute("data-theme", newTheme);
    
    localStorage.setItem("theme", newTheme); // Save knowledge of current theme
});