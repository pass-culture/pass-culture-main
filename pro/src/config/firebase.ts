export const firebaseConfig = {
  apiKey:
    process.env.REACT_APP_FIRBASE_API_KEY ||
    'AIzaSyAhXSv-Wk5I3hHAga5KhCe_SUhdmY-2eyQ',
  authDomain:
    process.env.REACT_APP_FIREBASE_AUTH_DOMAIN ||
    'passculture-pro.firebaseapp.com',
  projectId: process.env.FIREBASE_PROJECT_ID || 'passculture-pro',
  storageBucket:
    process.env.REACT_APP_FIREBASE_STORAGE_BUCKET ||
    'passculture-pro.appspot.com',
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID || '412444774135',
  appId:
    process.env.REACT_APP_FIREBASE_APP_ID ||
    '1:412444774135:web:0cd1b28CCCC6f9d6c54df2',
  measurementId: process.env.FIREBASE_MEASUREMENT_ID || 'G-FBPYNQPRF6',
}
