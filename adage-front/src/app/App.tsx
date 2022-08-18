import '@fontsource/barlow'
import '@fontsource/barlow/600.css'
import '@fontsource/barlow/700.css'
import '@fontsource/barlow/300.css'

import * as React from 'react'
import { useCallback, useEffect, useState } from 'react'

import { api as apiLegacy } from 'api/api'
import {
  AuthenticatedResponse,
  AdageFrontRoles,
  VenueResponse,
} from 'apiClient'
import { api } from 'apiClient/api'
import { UnauthenticatedError } from 'app/components/UnauthenticatedError/UnauthenticatedError'
import { logCatalogView } from 'repository/pcapi/pcapi'
import { LOGS_DATA } from 'utils/config'

import { AppLayout } from './AppLayout'
import {
  Notification,
  NotificationComponent,
  NotificationType,
} from './components/Layout/Notification/Notification'
import { LoaderPage } from './components/LoaderPage/LoaderPage'
import { FacetFiltersContextProvider } from './providers'

export const App = (): JSX.Element => {
  const [user, setUser] = useState<AuthenticatedResponse | null>()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [venueFilter, setVenueFilter] = useState<VenueResponse | null>(null)
  const [notification, setNotification] = useState<Notification | null>(null)

  useEffect(() => {
    api
      .authenticate()
      .then(user => setUser(user))
      .then(() => {
        const params = new URLSearchParams(window.location.search)
        const siret = params.get('siret')
        const venueId = Number(params.get('venue'))
        if (siret) {
          return apiLegacy
            .getAdageIframeGetVenueBySiret(siret)
            .then(venueFilter => setVenueFilter(venueFilter))
            .catch(() =>
              setNotification(
                new Notification(
                  NotificationType.error,
                  'Lieu inconnu. Tous les résultats sont affichés.'
                )
              )
            )
        }

        if (venueId && !Number.isNaN(venueId)) {
          return api
            .getVenueById(venueId)
            .then(venueFilter => setVenueFilter(venueFilter))
            .catch(() =>
              setNotification(
                new Notification(
                  NotificationType.error,
                  'Lieu inconnu. Tous les résultats sont affichés.'
                )
              )
            )
        }
      })
      .catch(() => setUser(null))
      .finally(() => {
        setIsLoading(false)
        if (LOGS_DATA) {
          logCatalogView()
        }
      })
  }, [])

  const removeVenueFilter = useCallback(() => setVenueFilter(null), [])

  if (isLoading) {
    return <LoaderPage />
  }

  return (
    <FacetFiltersContextProvider uai={user?.uai}>
      {notification && <NotificationComponent notification={notification} />}
      {user?.role &&
      [AdageFrontRoles.READONLY, AdageFrontRoles.REDACTOR].includes(
        user.role
      ) ? (
        <AppLayout
          removeVenueFilter={removeVenueFilter}
          user={user}
          venueFilter={venueFilter}
        />
      ) : (
        <UnauthenticatedError />
      )}
    </FacetFiltersContextProvider>
  )
}
