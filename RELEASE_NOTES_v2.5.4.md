# Release Notes - v2.5.4

## Highlights
- **Local Tailwind CSS Build**: Tailwind CSS is now built locally for both development and production. No CDN or external CSS dependencies required.
- **CSS Cleanup**: Removed legacy and unused CSS files. All styles are now served from `frontend/public/styles/output.css`.
- **Deployment Documentation Updated**: Production deployment docs now include instructions for building Tailwind CSS locally and ensuring only local assets are used.
- **Improved Dev Workflow**: Added scripts for building and watching Tailwind CSS. Development is now easier and more robust.
- **README Updated**: Added a section describing the new Tailwind CSS workflow for the team.

## Upgrade Notes
- Run `npm install` and `npm run build:css` before deploying or serving the frontend.
- Ensure your `index.html` references only `./styles/output.css` for styles.
- Remove any old references to `tailwind.min.css`, `tailwind.prod.css`, or similar files.

---

This release makes the frontend fully self-contained and production-ready with a modern, local-first CSS workflow. 