const FIELD_LABELS = [
  ["fullName", "Full name"],
  ["firstName", "First name"],
  ["lastName", "Last name"],
  ["email", "Email"],
  ["phone", "Phone"],
  ["city", "City"],
  ["country", "Country"],
  ["title", "Title"],
  ["linkedin", "LinkedIn"],
  ["github", "GitHub"],
  ["portfolio", "Portfolio"],
  ["cv", "CV link"],
  ["yearsFlutter", "Years in Flutter"],
  ["yearsSoftware", "Years in software"],
  ["dob", "Date of birth"],
  ["gender", "Gender"],
  ["nationality", "Nationality"],
  ["currentSalary", "Current salary"],
  ["expectedSalary", "Expected salary"]
];

const fieldsRoot = document.getElementById("fields");
const answersRoot = document.getElementById("answers");
const status = document.getElementById("status");

function answerCard(answer) {
  const card = document.createElement("div");
  card.className = "card";
  card.innerHTML = `
    <label>Question phrases <input class="q" type="text"></label>
    <label>Answer <textarea class="a"></textarea></label>
    <button class="link" type="button">Remove</button>
  `;
  card.querySelector(".q").value = answer.q || "";
  card.querySelector(".a").value = answer.a || "";
  card.querySelector("button").addEventListener("click", () => card.remove());
  return card;
}

function readProfile() {
  const fields = {};
  for (const input of fieldsRoot.querySelectorAll("input")) fields[input.dataset.key] = input.value.trim();
  const answers = [...answersRoot.querySelectorAll(".card")].map((card) => ({
    q: card.querySelector(".q").value.trim(),
    a: card.querySelector(".a").value.trim()
  })).filter((item) => item.q && item.a);
  return { fields, answers };
}

async function init() {
  const profile = await getProfile();
  for (const [key, label] of FIELD_LABELS) {
    const wrap = document.createElement("label");
    wrap.innerHTML = `${label}<input data-key="${key}" type="text">`;
    wrap.querySelector("input").value = profile.fields[key] || "";
    fieldsRoot.appendChild(wrap);
  }
  for (const answer of profile.answers) answersRoot.appendChild(answerCard(answer));
}

document.getElementById("add").addEventListener("click", () => {
  answersRoot.appendChild(answerCard({ q: "", a: "" }));
});

document.getElementById("save").addEventListener("click", async () => {
  await saveProfile(readProfile());
  status.textContent = "Saved";
});

init();
