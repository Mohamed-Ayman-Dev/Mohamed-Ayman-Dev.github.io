async function getProfile() {
  const data = await chrome.storage.local.get("profile");
  const seed = structuredClone(SEED);
  const current = data.profile;
  if (!current || !current.fields) {
    await chrome.storage.local.set({ profile: seed });
    return seed;
  }
  current.fields = current.fields || {};
  current.answers = current.answers || [];
  let changed = false;
  const staleValues = new Set([
    "30000-40000 EGP per month",
    "من 30000 إلى 40000 جنيه في الشهر",
    "3.5+",
    "3.5+ years in Flutter",
    "3.5+ years in Flutter, over 5 years in software",
    "أكتر من 3.5 سنة",
    "أكتر من 3.5 سنة Flutter، وأكتر من 5 سنين في السوفتوير"
  ]);
  for (const [key, value] of Object.entries(seed.fields)) {
    if (!current.fields[key] || staleValues.has(current.fields[key])) {
      if (current.fields[key] !== value) {
        current.fields[key] = value;
        changed = true;
      }
    }
  }
  const staleStarts = [
    "I have 3.5+ years shipping production Flutter apps to the App Store",
    "عندي أكتر من 3.5 سنة بنشر تطبيقات Flutter"
  ];
  for (const answer of seed.answers) {
    const key = answer.q.trim().toLowerCase();
    const existing = current.answers.find((item) => item.q.trim().toLowerCase() === key);
    if (!existing) {
      current.answers.push(answer);
      changed = true;
    } else if (existing.a !== answer.a && (existing.a === "4+" || existing.a === "3" || existing.a === "Cursor" || staleValues.has(existing.a) || staleStarts.some((start) => existing.a.startsWith(start)) || existing.a.includes("3.5+"))) {
      existing.a = answer.a;
      changed = true;
    }
  }
  if (changed) await chrome.storage.local.set({ profile: current });
  return current;
}

async function saveProfile(profile) {
  await chrome.storage.local.set({ profile });
}
