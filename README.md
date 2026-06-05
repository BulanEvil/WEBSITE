# Static Blog Demo

This is a plain static website used to test the publishing workflow before building the full company website.

## Preview Locally

Open `index.html` in a browser.

## Deploy To Cloudflare Pages

1. Push this folder to a GitHub repository.
2. In Cloudflare, open **Workers & Pages**.
3. Choose **Create application**.
4. Choose **Pages** and connect the GitHub repository.
5. Use these settings:
   - Framework preset: `None`
   - Build command: leave empty
   - Build output directory: `/`
6. Deploy.
7. Add your custom domain in the Pages project settings.

## Edit Content

- Main page content: `index.html`
- Visual style: `styles.css`
- Theme toggle: `script.js`
