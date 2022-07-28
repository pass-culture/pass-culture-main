import '@fontsource/barlow'
import '@fontsource/barlow/600.css'
import '@fontsource/barlow/700.css'
import '@fontsource/barlow/300.css'

import { MatomoProvider, createInstance } from '@datapunt/matomo-tracker-react'
import * as React from 'react'
import { useCallback, useEffect, useState } from 'react'
import { QueryCache, QueryClient, QueryClientProvider } from 'react-query'

import { api } from 'api/api'
import { AdageFrontRoles, AuthenticatedResponse, VenueResponse } from 'api/gen'
import { UnauthenticatedError } from 'app/components/UnauthenticatedError/UnauthenticatedError'
import {
  ACTIVATE_MATOMO_TRACKING,
  MATOMO_BASE_URL,
  MATOMO_SITE_ID,
} from 'utils/config'

import { AppLayout } from './AppLayout'
import {
  Notification,
  NotificationComponent,
  NotificationType,
} from './components/Layout/Notification/Notification'
import { LoaderPage } from './components/LoaderPage/LoaderPage'
import { FacetFiltersContextProvider } from './providers'

const instance = createInstance({
  urlBase: MATOMO_BASE_URL,
  siteId: parseInt(MATOMO_SITE_ID),
  disabled: ACTIVATE_MATOMO_TRACKING !== 'true',
  heartBeat: {
    active: true,
    seconds: 10,
  },
  linkTracking: false,
  configurations: {
    setSecureCookie: process.env.NODE_ENV !== 'development',
    setRequestMethod: 'POST',
  },
})

export const queryCache = new QueryCache()
export const queryClient = new QueryClient({
  queryCache,
  defaultOptions: {
    queries: {
      retry: 0,
    },
  },
})

export const App = (): JSX.Element => {
  const [user, setUser] = useState<AuthenticatedResponse | null>()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [venueFilter, setVenueFilter] = useState<VenueResponse | null>(null)
  const [notification, setNotification] = useState<Notification | null>(null)

  useEffect(() => {
    api
      .getAdageIframeAuthenticate()
      .then(user => setUser(user))
      .then(() => {
        const params = new URLSearchParams(window.location.search)
        const siret = params.get('siret')
        const venueId = Number(params.get('venue'))
        if (siret) {
          return api
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
            .getAdageIframeGetVenueById(venueId)
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
      .finally(() => setIsLoading(false))
  }, [])

  const removeVenueFilter = useCallback(() => setVenueFilter(null), [])

  if (isLoading) {
    return <LoaderPage />
  }

  return (
    <FacetFiltersContextProvider uai={user?.uai}>
      <QueryClientProvider client={queryClient}>
        {notification && <NotificationComponent notification={notification} />}
        {user?.role &&
        [AdageFrontRoles.Readonly, AdageFrontRoles.Redactor].includes(
          user.role
        ) ? (
          <MatomoProvider value={instance}>
            <AppLayout
              removeVenueFilter={removeVenueFilter}
              user={user}
              venueFilter={venueFilter}
            />
          </MatomoProvider>
        ) : (
          <UnauthenticatedError />
        )}
      </QueryClientProvider>
    </FacetFiltersContextProvider>
  )
}
