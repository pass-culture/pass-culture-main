import { type Dispatch, type SetStateAction, useEffect, useState } from 'react'
import { useLocation } from 'react-router'
import { v4 as uuidv4 } from 'uuid'

import { sendSentryCustomError } from '@/commons/utils/sendSentryCustomError'
import { storageAvailable } from '@/commons/utils/storageAvailable'

import {
  Consents,
  LOCAL_STORAGE_DEVICE_ID_KEY,
  orejimeConfig,
} from './orejimeConfig'

// biome-ignore lint/suspicious/noExplicitAny: Orejime comes from a loaded script
export const orejimeRef = { current: null as any }

function addListener(
  setConsentedToFirebase: Dispatch<SetStateAction<boolean>>,
  setConsentedToBeamer: Dispatch<SetStateAction<boolean>>
) {
  orejimeRef.current.manager.on(
    'update',
    (
      updatedConsents: { [key in Consents]: boolean },
      allConsents: { [key in Consents]: boolean }
    ) => {
      if (Object.keys(updatedConsents).length > 0) {
        setConsentedToFirebase(allConsents[Consents.FIREBASE])
        setConsentedToBeamer(allConsents[Consents.BEAMER])
      }
    }
  )
}

function initOrejimeConsent(
  setConsentedToFirebase: Dispatch<SetStateAction<boolean>>,
  setConsentedToBeamer: Dispatch<SetStateAction<boolean>>
) {
  setTimeout(() => {
    if (!globalThis.loadOrejime) {
      return
    }

    if (
      storageAvailable('localStorage') &&
      localStorage.getItem(LOCAL_STORAGE_DEVICE_ID_KEY) === null
    ) {
      localStorage.setItem(LOCAL_STORAGE_DEVICE_ID_KEY, uuidv4())
    }

    try {
      if (!orejimeRef.current || !document.cookie.includes('pc-pro-orejime')) {
        orejimeRef.current = globalThis.loadOrejime(orejimeConfig)
        addListener(setConsentedToFirebase, setConsentedToBeamer)
        setConsentedToFirebase(
          orejimeRef.current.manager.getConsent(Consents.FIREBASE) || false
        )
        setConsentedToBeamer(
          orejimeRef.current.manager.getConsent(Consents.BEAMER) || false
        )
      }
    } catch (e) {
      sendSentryCustomError(e)
      setConsentedToFirebase(false)
      setConsentedToBeamer(false)
    }
  })
}

export const useOrejime = () => {
  const location = useLocation()
  const [consentedToFirebase, setConsentedToFirebase] = useState(false)
  const [consentedToBeamer, setConsentedToBeamer] = useState(false)

  useEffect(() => {
    if (location.pathname.includes('/adage-iframe')) {
      setConsentedToFirebase(false)
      setConsentedToBeamer(false)

      return
    }

    if (globalThis.loadOrejime) {
      initOrejimeConsent(setConsentedToFirebase, setConsentedToBeamer)

      return
    }

    const handleScriptLoaded = () => {
      initOrejimeConsent(setConsentedToFirebase, setConsentedToBeamer)
    }

    globalThis.addEventListener('orejime-script-loaded', handleScriptLoaded, {
      once: true,
    })

    return () => {
      globalThis.removeEventListener(
        'orejime-script-loaded',
        handleScriptLoaded
      )
    }
  }, [location.pathname])

  return { consentedToBeamer, consentedToFirebase }
}
