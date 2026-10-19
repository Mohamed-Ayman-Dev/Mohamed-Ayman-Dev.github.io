const fillButton = document.getElementById("fill");
const status = document.getElementById("status");
const list = document.getElementById("list");

fillButton.addEventListener("click", async () => {
  status.textContent = "Filling…";
  list.innerHTML = "";
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab || !tab.id || !tab.url || tab.url.startsWith("chrome://") || tab.url.startsWith("chrome-extension://")) {
    status.textContent = "Open a normal web form first.";
    return;
  }
  const profile = await getProfile();
  await chrome.scripting.executeScript({ target: { tabId: tab.id }, files: ["fill.js"] });
  const [run] = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: (data) => globalThis.__devFill(data),
    args: [profile]
  });
  const filled = run && run.result ? run.result.filled : [];
  status.textContent = filled.length ? `Filled ${filled.length}` : "Nothing matched. Add the question in the profile.";
  for (const item of filled) {
    const li = document.createElement("li");
    li.textContent = item;
    list.appendChild(li);
  }
});

document.getElementById("options").addEventListener("click", () => {
  chrome.runtime.openOptionsPage();
});
