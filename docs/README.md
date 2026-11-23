# docs/ — GitHub Pages site

This folder is the published site. `index.html` is the landing page; `vendor-risk-assessment.html` and `control-crosswalk.html` are the interactive tools.

## Enable GitHub Pages

1. Push this repository to GitHub.
2. Repo **Settings → Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Branch: **`main`**, folder: **`/docs`**. Save.
5. After a minute the site is live at `https://2wake.github.io/empire-city-taxi-grc/`.

## Notes

- The project cards in `index.html` link to the repo folders at `github.com/2Wake/empire-city-taxi-grc/...`; the two tool cards are local to this folder.
- The tools are self-contained HTML — no build step, no dependencies beyond Google Fonts.
- All three pages support light/dark automatically and are responsive to phone width.
- The site serves only this `/docs` folder; the project write-ups live in the repo and are linked out to GitHub.
- The repository is named `empire-city-taxi-grc`, matching the fictional company **Empire City Taxi Co.**
