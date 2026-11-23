# docs/ — GitHub Pages site

This folder is the published site. `index.html` is the landing page; `vendor-risk-assessment.html` and `control-crosswalk.html` are the interactive tools.

## Enable GitHub Pages

1. Push this repository to GitHub.
2. Repo **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Branch: **`main`**, folder: **`/docs`**. Save.
5. After a minute the site is live at `https://YOUR-USERNAME.github.io/northlake-grc/`.

## One edit before you publish

In `index.html`, the four **project cards** link to the GitHub repo folders using a placeholder. Find-and-replace **`YOUR-USERNAME`** with your GitHub username so those links resolve. (The two tool cards are local and need no change.)

## Notes

- The tools are self-contained HTML — no build step, no dependencies beyond Google Fonts.
- All three pages support light/dark automatically and are responsive to phone width.
- The site serves only this `/docs` folder; the project write-ups live in the repo and are linked out to GitHub.
