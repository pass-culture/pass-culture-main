import * as firebase from '@firebase/app'

import {
  getAnalytics,
  initializeAnalytics,
  setUserId,
} from '@firebase/analytics'
import { useEffect, useState } from 'react'

import { logEvent as analyticsLogEvent } from '@firebase/analytics'
import { firebaseConfig } from 'config/firebase'

type logEventType = () => (
  event: string,
  params: { [key: string]: string }
) => void

export interface IUseAnalyticsReturn {
  currentUserId: string | undefined
  logEvent: logEventType | undefined
}

const useAnalytics = (
  currentUserId: string | undefined
): IUseAnalyticsReturn => {
  const [app, setApp] = useState<firebase.FirebaseApp | undefined>()
  const [logEvent, setLogEvent] = useState<logEventType>()
  useEffect(() => {
    if (!app) {
      const initializeApp = firebase.initializeApp(firebaseConfig)
      setApp(initializeApp)
      initializeAnalytics(initializeApp, {
        config: {
          send_page_view: false,
        },
      })
      setLogEvent(
        () =>
          (event: string, params: { [key: string]: string } = {}) => {
            analyticsLogEvent(getAnalytics(app), event, params)
          }
      )
    }
  }, [app])

  useEffect(() => {
    if (currentUserId) {
      setUserId(getAnalytics(app), currentUserId)
    }
  }, [app, currentUserId])

  return {
    currentUserId,
    logEvent,
  }
}

export default useAnalytics
