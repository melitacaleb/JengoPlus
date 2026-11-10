# JengoPlus Frontend (HTML + Bootstrap 5 + CSS)
Open `index.html` in a browser (or use the VS Code Live Server extension).

## Where to edit
- `css/style.css`: colours live in the variables at the top (light and dark).
- `js/layout.js`: navigation links and footer, shared by every page.
- `js/app.js`: page behaviour (demo only, swap for real API calls).
- `*.html`: one file per screen.

## First push (Git Bash)
    git init && git branch -M main
    git remote add origin https://github.com/YOUR-USER/YOUR-REPO.git
    git add -A && git commit -m "Add frontend shell" && git push -u origin main
## Every later change
    ./push.sh "describe your change"
