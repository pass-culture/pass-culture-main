import {
  getAnalytics,
  initializeAnalytics,
  setUserId,
  logEvent as analyticsLogEvent,
  isSupported,
} from '@firebase/analytics'
import * as firebase from '@firebase/app'
import { useContext, useEffect, useState } from 'react'

import { firebaseConfig } from 'config/firebase'
import { AnalyticsContext } from 'context/analyticsContext'

export const useConfigureAnalytics = (currentUserId: string | undefined) => {
  const [app, setApp] = useState<firebase.FirebaseApp | undefined>()
  const [isFirebaseSupported, setIsFirebaseSupported] = useState<boolean>(false)
  const { setLogEvent } = useAnalytics()

  useEffect(() => {
    async function initializeIfNeeded() {
      setIsFirebaseSupported(await isSupported())
    }
    initializeIfNeeded()
  }, [])

  useEffect(() => {
    if (!app && isFirebaseSupported) {
      const initializeApp = firebase.initializeApp(firebaseConfig)
      setApp(initializeApp)
      isFirebaseSupported &&
        initializeAnalytics(initializeApp, {
          config: {
            send_page_view: false,
          },
        })

      setLogEvent &&
        setLogEvent(
          () =>
            (
              event: string,
              params:
                | { [key: string]: string | boolean | string[] }
                | Record<string, never> = {}
            ) => {
              analyticsLogEvent(getAnalytics(app), event, params)
            }
        )
    }
  }, [app, isFirebaseSupported])

  useEffect(() => {
    if (app && currentUserId && isFirebaseSupported) {
      setUserId(getAnalytics(app), currentUserId)
    }
  }, [app, currentUserId])
}

function useAnalytics() {
  return useContext(AnalyticsContext)
}

export default useAnalytics
