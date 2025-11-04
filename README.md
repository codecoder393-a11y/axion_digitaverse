This is a small local backend to host user avatars for the Axion app.

Endpoints added (do not remove any existing backend endpoints in your real backend):

- POST /api/upload-avatar
  - form-data: avatar (file), address (string)
  - returns JSON: { address, url }

- GET /api/avatar/:address
  - returns JSON: { address, url } or 404

- Static files served at /uploads/*

Run locally:

1) cd backend
2) npm install
3) npm start

This is optional — your main production backend can continue to operate. The app is written to try the production BACKEND_URL first; you can also run this local backend and point the app to it for local testing by changing `app/(tabs)/api.ts` BACKEND_URL.
