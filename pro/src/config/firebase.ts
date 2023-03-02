export const firebaseConfig = {
  apiKey:
    process.env.REACT_APP_FIREBASE_PUBLIC_API_KEY || 'AIzaSyDv-igPDFDCvZDofcjiZ-TUBLwB3sIcjZ0',
  authDomain:
    process.env.REACT_APP_FIREBASE_AUTH_DOMAIN || 'pc-pro-testing.firebaseapp.com',
  projectId: process.env.FIREBASE_PROJECT_ID || 'pc-pro-testing',
  storageBucket:
    process.env.REACT_APP_FIREBASE_STORAGE_BUCKET || 'pc-pro-testing.appspot.com',
  messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID || '1086794247971',
  appId:
    process.env.REACT_APP_FIREBASE_APP_ID || '1:1086794247971:web:63ee819ffc368e0d102696',
  measurementId: process.env.FIREBASE_MEASUREMENT_ID || 'G-S7C0MDBZT7',
}
