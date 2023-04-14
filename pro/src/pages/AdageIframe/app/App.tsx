import * as React from 'react'
import { useCallback, useEffect, useState } from 'react'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
  VenueResponse,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { LOGS_DATA } from 'utils/config'

import { initAlgoliaAnalytics } from '../libs/initAlgoliaAnalytics'

import { AppLayout } from './AppLayout'
import {
  Notification,
  NotificationComponent,
  NotificationType,
} from './components/Layout/Notification/Notification'
import { LoaderPage } from './components/LoaderPage/LoaderPage'
import { UnauthenticatedError } from './components/UnauthenticatedError/UnauthenticatedError'
import { FacetFiltersContextProvider } from './providers'

export const App = (): JSX.Element => {
  const [user, setUser] = useState<AuthenticatedResponse | null>()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [venueFilter, setVenueFilter] = useState<VenueResponse | null>(null)
  const [notification, setNotification] = useState<Notification | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const siret = params.get('siret')
    const venueId = Number(params.get('venue'))
    const getRelativeOffers = params.get('all') === 'true'
    apiAdage
      .authenticate()
      .then(user => setUser(user))
      .then(() => {
        if (siret) {
          return apiAdage
            .getVenueBySiret(siret, getRelativeOffers)
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
          return apiAdage
            .getVenueById(venueId, getRelativeOffers)
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
        return null
      })
      .catch(() => setUser(null))
      .finally(() => {
        setIsLoading(false)
        if (LOGS_DATA) {
          apiAdage.logCatalogView({
            source: siret || venueId ? 'partnersMap' : 'homepage',
          })
        }
      })
  }, [])

  const removeVenueFilter = useCallback(() => setVenueFilter(null), [])

  useEffect(() => {
    initAlgoliaAnalytics()
  }, [])

  if (isLoading) {
    return <LoaderPage />
  }

  return (
    <FacetFiltersContextProvider
      departmentCode={user?.departmentCode}
      uai={user?.uai}
    >
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
