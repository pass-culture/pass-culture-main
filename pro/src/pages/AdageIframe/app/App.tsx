import * as React from 'react'
import { useCallback, useEffect, useId, useState } from 'react'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
  VenueResponse,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import useActiveFeature from 'hooks/useActiveFeature'
import { LOGS_DATA } from 'utils/config'
import { removeParamsFromUrl } from 'utils/removeParamsFromUrl'

import { initAlgoliaAnalytics } from '../libs/initAlgoliaAnalytics'

import { AppLayout } from './components/AppLayout/AppLayout'
import {
  Notification,
  NotificationComponent,
  NotificationType,
} from './components/Layout/Notification/Notification'
import { LoaderPage } from './components/LoaderPage/LoaderPage'
import { UnauthenticatedError } from './components/UnauthenticatedError/UnauthenticatedError'
import { OldAppLayout } from './OldAppLayout'
import {
  FacetFiltersContextProvider,
  FiltersContextProvider,
} from './providers'
import { AdageUserContext } from './providers/AdageUserContext'

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
            AdageHeaderFrom: removeParamsFromUrl(location.pathname),
            source: siret || venueId ? 'partnersMap' : 'homepage',
          })
        }
      })
  }, [])

  const removeVenueFilter = useCallback(() => setVenueFilter(null), [])

  const uniqueId = useId()
  const isNewHeaderActive = useActiveFeature('WIP_ENABLE_NEW_ADAGE_HEADER')
  useEffect(() => {
    initAlgoliaAnalytics(uniqueId)
  }, [])

  if (isLoading) {
    return <LoaderPage />
  }

  if (!user) {
    return <UnauthenticatedError />
  }

  return (
    <AdageUserContext.Provider value={{ adageUser: user }}>
      <FiltersContextProvider venueFilter={venueFilter}>
        <FacetFiltersContextProvider
          departmentCode={user?.departmentCode}
          uai={user?.uai}
          venueFilter={venueFilter}
        >
          {notification && (
            <NotificationComponent notification={notification} />
          )}
          {user?.role &&
          [AdageFrontRoles.READONLY, AdageFrontRoles.REDACTOR].includes(
            user.role
          ) ? (
            isNewHeaderActive ? (
              <AppLayout
                removeVenueFilter={removeVenueFilter}
                venueFilter={venueFilter}
              />
            ) : (
              <OldAppLayout
                removeVenueFilter={removeVenueFilter}
                venueFilter={venueFilter}
              />
            )
          ) : (
            <UnauthenticatedError />
          )}
        </FacetFiltersContextProvider>
      </FiltersContextProvider>
    </AdageUserContext.Provider>
  )
}
