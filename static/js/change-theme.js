function setTheme() {
  const themeLink = document.getElementById("theme-link");
  const href = themeLink.getAttribute("href");
  const url = new URL(href, window.location.origin);
  const segments = url.pathname.split("/");
  const currentTheme = segments[segments.length - 1];
  segments[segments.length - 1] =
    `${currentTheme.includes("light") ? "dark" : "light"}.css`;
  url.pathname = segments.join("/");
  themeLink.setAttribute("href", url.toString());
}
window.setTheme = setTheme;
