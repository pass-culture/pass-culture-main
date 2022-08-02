import {
  getAnalytics,
  initializeAnalytics,
  setUserId,
  logEvent as analyticsLogEvent,
} from '@firebase/analytics'
import * as firebase from '@firebase/app'
import { useContext, useEffect, useState } from 'react'

import { firebaseConfig } from 'config/firebase'
import { AnalyticsContext } from 'context/analyticsContext'

export const useConfigureAnalytics = (
  currentUserId: string | undefined
): void => {
  const [app, setApp] = useState<firebase.FirebaseApp | undefined>()
  const { setLogEvent } = useAnalytics()
  useEffect(() => {
    if (!app) {
      const initializeApp = firebase.initializeApp(firebaseConfig)
      setApp(initializeApp)
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
  }, [app])

  useEffect(() => {
    if (app && currentUserId) {
      setUserId(getAnalytics(app), currentUserId)
    }
  }, [app, currentUserId])
}

function useAnalytics() {
  return useContext(AnalyticsContext)
}

export default useAnalytics
