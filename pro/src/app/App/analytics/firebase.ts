/* istanbul ignore file */

import {
  logEvent as analyticsLogEvent,
  getAnalytics,
  initializeAnalytics,
  isSupported,
  setUserId,
} from '@firebase/analytics'
import * as firebase from '@firebase/app'
import {
  fetchAndActivate,
  getRemoteConfig,
  type RemoteConfig,
} from '@firebase/remote-config'
import { useCallback, useEffect, useState } from 'react'
import { useLocation } from 'react-router'

import { isError } from '@/apiClient/helpers'
import { firebaseConfig } from '@/commons/config/firebase'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useUtmQueryParams } from '@/commons/hooks/useUtmQueryParams'

let firebaseApp: firebase.FirebaseApp | undefined
let firebaseRemoteConfig: RemoteConfig | undefined

export const destroyFirebase = async () => {
  if (firebaseApp) {
    await firebase.deleteApp(firebaseApp)
    firebaseApp = undefined
    firebaseRemoteConfig = undefined
  }
}

export const useFirebase = (consentedToFirebase: boolean) => {
  const currentUser = useAppSelector((state) => state.user.currentUser)

  const [isFirebaseInitialized, setIsFirebaseInitialized] =
    useState<boolean>(false)

  useEffect(() => {
    const loadAnalytics = async () => {
      const isFirebaseSupported = await isSupported()
      if (!isFirebaseSupported) {
        return
      }

      firebaseApp = firebase.initializeApp(firebaseConfig)
      setIsFirebaseInitialized(true)

      try {
        initializeAnalytics(firebaseApp, { config: { send_page_view: false } })
        firebaseRemoteConfig = getRemoteConfig(firebaseApp)
        await fetchAndActivate(firebaseRemoteConfig)
      } catch (err) {
        const errorName = isError(err) ? err.name : ''
        const errorMessage = isError(err) ? err.message : String(err)

        const isFirebaseStorageError =
          errorName === 'FirebaseError' &&
          errorMessage.includes('remoteconfig/storage-open')

        // Throw any error that is not 'InvalidStateError' or a Firebase storage error
        if (errorName !== 'InvalidStateError' && !isFirebaseStorageError) {
          throw err
        }
      }
    }

    if (consentedToFirebase) {
      if (!firebaseApp) {
        loadAnalytics()
      }
    } else {
      if (firebaseApp) {
        destroyFirebase()
        setIsFirebaseInitialized(false)
      }
    }
  }, [consentedToFirebase])

  useEffect(() => {
    if (isFirebaseInitialized) {
      setUserId(getAnalytics(firebaseApp), currentUser?.id.toString() ?? null)
    }
  }, [currentUser, isFirebaseInitialized])
}

const eventsQueue: {
  event: string
  params?: {
    [key: string]:
      | string
      | string[]
      | number
      | boolean
      | undefined
      // biome-ignore lint/suspicious/noExplicitAny: Generic params type.
      | Record<string, any>
  }
  utmParameters: {
    traffic_campaign?: string
    traffic_medium?: string
    traffic_source?: string
  }
  pathname: string
}[] = []

// TODO (igabriele, 2026-05-12): This should be a pure function "grabbing" store values + using native `location` when called, there is absolutely no need to use a hook here which will re-render on every state change.
export const useAnalytics = () => {
  const selectedPartnerVenue = useAppSelector(
    (state) => state.user.selectedPartnerVenue
  )
  const selectedAdminOfferer = useAppSelector(
    (state) => state.user.selectedAdminOfferer
  )
  const location = useLocation()
  const utmParameters = useUtmQueryParams()

  const logEvent = useCallback(
    (
      event: string,
      params?: {
        [key: string]:
          | string
          | string[]
          | number
          | boolean
          | undefined
          // biome-ignore lint/suspicious/noExplicitAny: Generic params type.
          | Record<string, any>
      }
    ) => {
      if (!firebaseApp || !firebaseRemoteConfig) {
        eventsQueue.push({
          event,
          params,
          utmParameters,
          pathname: globalThis.location.href,
        })
        return
      } else {
        while (eventsQueue.length) {
          const stored = eventsQueue.pop()
          if (stored) {
            analyticsLogEvent(getAnalytics(firebaseApp), stored.event, {
              ...stored.params,
              page_location: stored.pathname,
              offererId: selectedAdminOfferer?.id.toString() ?? null,
              venueId: selectedPartnerVenue?.id.toString() ?? null,
              ...stored.utmParameters,
            })
          }
        }
      }

      analyticsLogEvent(getAnalytics(firebaseApp), event, {
        from: location.pathname,
        offererId: selectedAdminOfferer?.id.toString() ?? null,
        venueId: selectedPartnerVenue?.id.toString() ?? null,
        ...params,
        ...utmParameters,
      })
    },
    [
      location.pathname,
      selectedAdminOfferer,
      selectedPartnerVenue,
      utmParameters,
    ]
  )

  return { logEvent }
}
