# Mohamed Ayman — Portfolio

Personal portfolio site for Mohamed Ayman, Senior Flutter Developer.

Single-page static site — plain HTML/CSS/JS, no build step required.

## Run locally

Open `index.html` directly in a browser, or serve it:

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Project screenshots

Each project card looks for a screenshot in `assets/` (e.g. `assets/invastro.jpg`, `assets/vero.jpg`).
If the file doesn't exist, the card automatically falls back to a colored gradient with an icon — so missing screenshots never break the page.

To add a screenshot: export a portrait app screenshot (JPG/PNG, ideally ≤ 300 KB) and save it to `assets/` using the name referenced in the `projects` array in `index.html`.

Recommended: compress screenshots before adding them, e.g. with [Squoosh](https://squoosh.app).

## Deploy to GitHub Pages

1. Create a repository on GitHub (e.g. `portfolio`).
2. Push this project:

```bash
git remote add origin git@github.com:Mohamed-Ayman-Dev/portfolio.git
git push -u origin main
```

3. On GitHub: **Settings → Pages → Source: Deploy from a branch → main / (root)**.
4. The site will be live at `https://mohamed-ayman-dev.github.io/portfolio/`.

> If you rename the repo to `Mohamed-Ayman-Dev.github.io`, the site is served at the root domain instead — update the `canonical` and `og:url` meta tags in `index.html` accordingly.
