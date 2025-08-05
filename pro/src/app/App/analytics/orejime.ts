import { sendSentryCustomError } from 'commons/utils/sendSentryCustomError'
import { storageAvailable } from 'commons/utils/storageAvailable'
import { useEffect, useState } from 'react'
import { useLocation } from 'react-router'
import { v4 as uuidv4 } from 'uuid'

import {
  Consents,
  LOCAL_STORAGE_DEVICE_ID_KEY,
  orejimeConfig,
} from './orejimeConfig'

export let orejime: any = null

export const useOrejime = () => {
  const location = useLocation()
  const [consentedToFirebase, setConsentedToFirebase] = useState(false)
  const [consentedToBeamer, setConsentedToBeamer] = useState(false)

  function addListener() {
    orejime.manager.on(
      'update',
      function (
        updatedConsents: { [key in Consents]: boolean },
        allConsents: { [key in Consents]: boolean }
      ) {
        if (Object.keys(updatedConsents).length > 0) {
          setConsentedToFirebase(allConsents[Consents.FIREBASE])
          setConsentedToBeamer(allConsents[Consents.BEAMER])
        }
      }
    )
  }

  useEffect(() => {
    // Initialize cookie consent modal
    if (location.pathname.indexOf('/adage-iframe') === -1) {
      setTimeout(() => {
        if (
          storageAvailable('localStorage') &&
          localStorage.getItem(LOCAL_STORAGE_DEVICE_ID_KEY) === null
        ) {
          localStorage.setItem(LOCAL_STORAGE_DEVICE_ID_KEY, uuidv4())
        }

        try {
          if (!orejime) {
            orejime = window.loadOrejime(orejimeConfig)
            addListener()
            setConsentedToFirebase(
              orejime.manager.getConsent(Consents.FIREBASE) || false
            )
            setConsentedToBeamer(
              orejime.manager.getConsent(Consents.BEAMER) || false
            )
          } else if (!document.cookie.includes('orejime')) {
            // We force the banner to be displayed again if the cookie was deleted somehow
            orejime.manager.clearConsents()
            orejime = window.loadOrejime(orejimeConfig)
            addListener()
          }
        } catch (e) {
          sendSentryCustomError(e)
          setConsentedToFirebase(false)
          setConsentedToBeamer(false)
        }
      })
    } else {
      setConsentedToFirebase(false)
      setConsentedToBeamer(false)
    }
  }, [location.pathname])

  return { consentedToBeamer, consentedToFirebase }
}
