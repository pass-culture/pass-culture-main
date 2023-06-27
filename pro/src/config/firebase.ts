export const firebaseConfig = {
  apiKey:
    import.meta.env.VITE_ASE_PUBLIC_API_KEY ||
    'AIzaSyAhXSv-Wk5I3hHAga5KhCe_SUhdmY-2eyQ',
  authDomain:
    import.meta.env.VITE_ASE_AUTH_DOMAIN || 'passculture-pro.firebaseapp.com',
  projectId: import.meta.env.VITE_ASE_PROJECT_ID || 'passculture-pro',
  storageBucket:
    import.meta.env.VITE_ASE_STORAGE_BUCKET || 'passculture-pro.appspot.com',
  messagingSenderId:
    import.meta.env.VITE_ASE_MESSAGING_SENDER_ID || '412444774135',
  appId:
    import.meta.env.VITE_ASE_APP_ID ||
    '1:412444774135:web:0cd1b28CCCC6f9d6c54df2',
  measurementId: import.meta.env.VITE_ASE_MEASUREMENT_ID || 'G-FBPYNQPRF6',
}
