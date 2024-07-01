// @ts-expect-error no types for this lib yet
import * as Orejime from 'orejime'
import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { v4 as uuidv4 } from 'uuid'

import { localStorageAvailable } from 'utils/localStorageAvailable'
import { sendSentryCustomError } from 'utils/sendSentryCustomError'

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

  useEffect(() => {
    // Initialize cookie consent modal
    if (location.pathname.indexOf('/adage-iframe') === -1) {
      setTimeout(() => {
        if (
          localStorageAvailable() &&
          localStorage.getItem(LOCAL_STORAGE_DEVICE_ID_KEY) === null
        ) {
          localStorage.setItem(LOCAL_STORAGE_DEVICE_ID_KEY, uuidv4())
        }

        try {
          orejime = Orejime.init(orejimeConfig)
        } catch (e) {
          sendSentryCustomError(e)
          setConsentedToFirebase(false)
          setConsentedToBeamer(false)
        }

        if (orejime !== null) {
          // Set the consent on consent change
          orejime.internals.manager.watch({
            update: ({
              consents,
            }: {
              consents: { [key in Consents]: boolean }
            }) => {
              setConsentedToFirebase(consents[Consents.FIREBASE])
              setConsentedToBeamer(consents[Consents.BEAMER])
            },
          })
          setConsentedToFirebase(
            orejime.internals.manager.consents[Consents.FIREBASE]
          )
          setConsentedToBeamer(
            orejime.internals.manager.consents[Consents.BEAMER]
          )

          // We force the banner to be displayed again if the cookie was deleted somehow
          if (!document.cookie.includes('orejime')) {
            orejime.internals.manager.confirmed = false
            orejime = Orejime.init(orejimeConfig)
          }
        }
      })
    } else {
      setConsentedToFirebase(false)
      setConsentedToBeamer(false)
    }
  }, [location.pathname])

  return { consentedToBeamer, consentedToFirebase }
}
