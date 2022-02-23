import { getAnalytics } from '@firebase/analytics'
import * as firebase from '@firebase/app'
import { useRef } from 'react'

import { firebaseConfig } from 'config/firebase'

const useAnalytics = (): void => {
  const app = useRef<firebase.FirebaseApp>()

  if (!app.current) {
    app.current = firebase.initializeApp(firebaseConfig)
  }

  const analyticsProvider = getAnalytics(app.current)
}

export default useAnalytics
