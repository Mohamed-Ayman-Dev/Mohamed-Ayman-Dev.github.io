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

The site is published as a GitHub **user site**, so the repository must be named
`Mohamed-Ayman-Dev.github.io` and Pages serves the default branch at the root domain.

```bash
gh auth login                      # one time
gh repo create Mohamed-Ayman-Dev.github.io --public --source=. --remote=origin --push
```

Pages turns itself on for user-site repositories; the site goes live at
`https://mohamed-ayman-dev.github.io/` within a minute or two of the first push.

After that, deploying is just:

```bash
git add -A && git commit -m "..." && git push
```

> The `canonical`, `og:url` and `og:image` meta tags in `index.html` are absolute URLs
> pointing at that domain. If the repository is ever renamed to a normal project repo,
> those three tags need the `/<repo-name>/` path added back.
