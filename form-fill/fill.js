globalThis.__devFill = function (profile) {
  const STOP = new Set(["the", "and", "you", "your", "have", "with", "for", "this", "that", "from", "any", "are", "was", "were", "has", "had", "about", "into", "our", "all", "في", "من", "على", "عن", "مع", "هل", "ما", "هو", "هي", "انت", "أنت"]);
  const FIELD_KEYS = [
    { key: "email", words: ["email", "e-mail"] },
    { key: "phone", words: ["phone", "mobile", "telephone", "whatsapp"] },
    { key: "firstName", words: ["first name", "given name"] },
    { key: "lastName", words: ["last name", "surname", "family name"] },
    { key: "fullName", words: ["full name", "your name", "name"] },
    { key: "linkedin", words: ["linkedin"] },
    { key: "github", words: ["github"] },
    { key: "portfolio", words: ["portfolio", "personal site", "website", "personal website"] },
    { key: "cv", words: ["resume", "cv", "curriculum"] },
    { key: "city", words: ["city"] },
    { key: "country", words: ["country"] },
    { key: "title", words: ["current designation", "job title", "current title", "current role", "designation", "position"] },
    { key: "yearsFlutter", words: ["years of flutter", "flutter experience", "years in flutter"] },
    { key: "yearsSoftware", words: ["years of experience", "years in software", "total experience"] },
    { key: "dob", words: ["date of birth", "birth date", "dob", "تاريخ الميلاد", "تاريخ ميلاد"] },
    { key: "gender", words: ["gender", "الجنس"] },
    { key: "nationality", words: ["nationality", "الجنسية"] },
    { key: "currentSalary", words: ["current ctc", "current salary", "current monthly salary", "الراتب الحالي", "راتبك الحالي"] },
    { key: "expectedSalary", words: ["expected ctc", "expected salary", "expected monthly salary", "salary expectation", "desired salary", "الراتب المتوقع", "الراتب المطلوب"] }
  ];

  function tokens(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/[^\u0600-\u06FFa-z0-9+ ]/g, " ")
      .split(/\s+/)
      .filter((word) => word.length > 1 && !STOP.has(word));
  }

  function includesPhrase(text, phrase) {
    return text.toLowerCase().includes(phrase.toLowerCase());
  }

  function fieldValue(label) {
    const text = label.toLowerCase();
    let best = null;
    for (const item of FIELD_KEYS) {
      for (const phrase of item.words) {
        if (!includesPhrase(text, phrase)) continue;
        if ((item.key === "country" || item.key === "nationality") && /code|currency/.test(text)) continue;
        const score = phrase.length;
        if (!best || score > best.score) best = { score, value: profile.fields[item.key] || "" };
      }
    }
    return best && best.value ? best.value : "";
  }

  function answerFor(label) {
    const labelTokens = new Set(tokens(label));
    const labelText = label.toLowerCase();
    let best = null;
    for (const item of profile.answers || []) {
      const phrase = item.q.trim().toLowerCase();
      if (phrase && labelText.includes(phrase)) {
        const score = 1 + phrase.length / 1000;
        if (!best || score > best.score) best = { score, value: item.a };
        continue;
      }
      const words = tokens(item.q);
      if (!words.length) continue;
      let hits = 0;
      for (const word of words) if (labelTokens.has(word)) hits += 1;
      const single = words.length === 1 && words[0].length >= 5 && labelTokens.has(words[0]);
      const score = hits / words.length;
      if ((single || (hits >= 2 && score >= 0.45)) && (!best || score > best.score)) {
        best = { score, value: item.a };
      }
    }
    return best ? best.value : "";
  }

  function textOf(node) {
    return (node && node.innerText ? node.innerText : "").replace(/\s+/g, " ").trim();
  }

  function isChoice(el) {
    const type = (el.getAttribute && el.getAttribute("type") || "").toLowerCase();
    const role = (el.getAttribute && el.getAttribute("role") || "").toLowerCase();
    return type === "radio" || type === "checkbox" || role === "radio" || role === "checkbox";
  }

  function questionText(el) {
    const group = el.closest && el.closest("[role='radiogroup'], [role='group'], [role='listitem']");
    if (group) {
      const labelledby = group.getAttribute("aria-labelledby");
      if (labelledby) {
        const text = labelledby.split(/\s+/).map((id) => textOf(document.getElementById(id))).filter(Boolean).join(" ");
        if (text) return text.replace(/\*/g, "").trim();
      }
      const title = group.querySelector(".M7eMe, [role='heading']");
      if (title && !title.contains(el)) {
        const titleText = textOf(title).replace(/\*/g, "").trim();
        if (titleText) return titleText;
      }
    }
    if (!isChoice(el)) {
      const labelledby = el.getAttribute && el.getAttribute("aria-labelledby");
      if (labelledby) {
        const text = labelledby.split(/\s+/).map((id) => textOf(document.getElementById(id))).filter(Boolean).join(" ");
        if (text) return text;
      }
      if (el.id) {
        const label = document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
        if (label) return textOf(label);
      }
      const ownLabel = el.closest && el.closest("label");
      if (ownLabel && textOf(ownLabel).length < 120) return textOf(ownLabel);
    }
    let node = el.parentElement;
    for (let i = 0; i < 8 && node; i += 1) {
      for (const heading of node.querySelectorAll("[role='heading'], legend, h2, h3")) {
        if (heading.contains(el)) continue;
        const follows = heading.compareDocumentPosition(el) & Node.DOCUMENT_POSITION_FOLLOWING;
        const headingText = textOf(heading);
        if (follows && headingText.length > 3 && headingText.length < 400) return headingText;
      }
      node = node.parentElement;
    }
    return (el.getAttribute && (el.getAttribute("aria-label") || el.getAttribute("placeholder") || el.getAttribute("name"))) || "";
  }

  function optionText(el) {
    const dataValue = el.getAttribute && el.getAttribute("data-value");
    if (dataValue && dataValue.length < 80) return dataValue;
    const aria = el.getAttribute && el.getAttribute("aria-label");
    if (aria && aria.length < 80) return aria;
    const own = textOf(el);
    if (own && own.length < 80) return own;
    const sibling = el.nextElementSibling;
    const siblingText = textOf(sibling);
    if (siblingText && siblingText.length < 80) return siblingText;
    return el.value || "";
  }

  function sameOption(option, part) {
    const clean = (value) => value.toLowerCase().replace(/\s+/g, "").replace("＋", "+");
    return clean(option) === clean(part);
  }

  function mark(el) {
    el.style.outline = "2px solid #1f8a4c";
    el.style.outlineOffset = "2px";
  }

  function setText(el, value) {
    if (!value || (el.value && String(el.value).trim())) return false;
    const type = (el.getAttribute("type") || "").toLowerCase();
    if (type === "date" && /^\d{2}\/\d{2}\/\d{4}$/.test(value)) {
      const [day, month, year] = value.split("/");
      value = `${year}-${month}-${day}`;
    }
    if (type === "number") {
      const match = String(value).match(/\d+/);
      if (!match) return false;
      value = match[0];
    }
    el.focus();
    el.value = value;
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
    mark(el);
    return true;
  }

  function isOn(el) {
    return el.checked || el.getAttribute("aria-checked") === "true";
  }

  function press(el) {
    const rect = el.getBoundingClientRect();
    const opts = {
      bubbles: true,
      cancelable: true,
      view: window,
      clientX: rect.left + rect.width / 2,
      clientY: rect.top + Math.min(rect.height / 2, 12),
      button: 0
    };
    el.dispatchEvent(new PointerEvent("pointerdown", { ...opts, pointerId: 1, pointerType: "mouse", isPrimary: true }));
    el.dispatchEvent(new MouseEvent("mousedown", opts));
    el.dispatchEvent(new PointerEvent("pointerup", { ...opts, pointerId: 1, pointerType: "mouse", isPrimary: true }));
    el.dispatchEvent(new MouseEvent("mouseup", opts));
    el.dispatchEvent(new MouseEvent("click", opts));
  }

  function choose(el) {
    if (isOn(el)) return false;
    if (el.matches && el.matches("input[type='radio']")) {
      el.checked = true;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }
    press(el);
    if (!isOn(el)) {
      const action = el.closest && el.closest("[jsaction]");
      if (action && action !== el) press(action);
    }
    if (!isOn(el) && el.parentElement && el.parentElement !== el) press(el.parentElement);
    mark(el);
    return true;
  }

  const filled = [];
  const textFields = [...document.querySelectorAll("input, textarea, select")].filter((el) => {
    const type = (el.getAttribute("type") || el.tagName).toLowerCase();
    return !["hidden", "password", "file", "submit", "button", "reset", "image", "radio", "checkbox"].includes(type);
  });

  for (const el of textFields) {
    const label = questionText(el);
    const value = fieldValue(label) || answerFor(label);
    if (!value || value.length > 400 && el.tagName !== "TEXTAREA") continue;
    if (el.tagName === "SELECT") {
      const option = [...el.options].find((item) => item.text.trim().toLowerCase() === value.trim().toLowerCase());
      if (!option || el.value) continue;
      el.value = option.value;
      el.dispatchEvent(new Event("change", { bubbles: true }));
      mark(el);
      filled.push(label.slice(0, 80));
      continue;
    }
    if (setText(el, value)) filled.push(label.slice(0, 80));
  }

  const choices = [...document.querySelectorAll("[role='radio'], [role='checkbox'], input[type='radio'], input[type='checkbox']")].filter((el) => {
    if (el.matches("input") && el.closest("[role='radio'], [role='checkbox']")) return false;
    return true;
  });
  const groups = new Map();
  for (const el of choices) {
    const box = el.closest("[role='radiogroup'], [role='group'], fieldset, [role='listitem']") || el.parentElement;
    if (!groups.has(box)) groups.set(box, []);
    groups.get(box).push(el);
  }

  for (const [box, items] of groups) {
    const label = questionText(items[0]) || textOf(box);
    const value = answerFor(label);
    if (!value || value.length > 80) continue;
    const accepted = value.split(",").map((part) => part.trim().toLowerCase()).filter(Boolean);
    const radio = items.some((el) => (el.getAttribute("role") || el.type || "").toLowerCase() === "radio");
    const hits = items.filter((el) => {
      const option = optionText(el).toLowerCase();
      return option && accepted.some((part) => sameOption(option, part));
    });
    const picked = radio ? hits.slice(0, 1) : hits;
    for (const el of picked) {
      if (choose(el)) filled.push(label.slice(0, 80) + " → " + optionText(el));
    }
  }

  return { filled: filled.filter(Boolean) };
};
