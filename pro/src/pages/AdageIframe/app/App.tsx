import * as React from 'react'
import { useCallback, useEffect, useId, useState } from 'react'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
  VenueResponse,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import useNotification from 'hooks/useNotification'
import { LOGS_DATA } from 'utils/config'
import { removeParamsFromUrl } from 'utils/removeParamsFromUrl'

import { initAlgoliaAnalytics } from '../libs/initAlgoliaAnalytics'

import { AppLayout } from './components/AppLayout/AppLayout'
import { LoaderPage } from './components/LoaderPage/LoaderPage'
import { UnauthenticatedError } from './components/UnauthenticatedError/UnauthenticatedError'
import {
  FacetFiltersContextProvider,
  FiltersContextProvider,
} from './providers'
import { AdageUserContextProvider } from './providers/AdageUserContext'

export const App = (): JSX.Element => {
  const [user, setUser] = useState<AuthenticatedResponse | null>()
  const [isLoading, setIsLoading] = useState<boolean>(true)
  const [venueFilter, setVenueFilter] = useState<VenueResponse | null>(null)

  const notification = useNotification()

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const siret = params.get('siret')
    const venueId = Number(params.get('venue'))
    const getRelativeOffers = params.get('all') === 'true'
    apiAdage
      .authenticate()
      .then(user => setUser(user))
      .then(async () => {
        if (siret) {
          try {
            const result = await apiAdage.getVenueBySiret(
              siret,
              getRelativeOffers
            )
            return setVenueFilter(result)
          } catch {
            notification.error(
              'Lieu inconnu. Tous les résultats sont affichés.'
            )
          }
        }

        if (venueId && !Number.isNaN(venueId)) {
          try {
            const result = await apiAdage.getVenueById(
              venueId,
              getRelativeOffers
            )

            return setVenueFilter(result)
          } catch {
            notification.error(
              'Lieu inconnu. Tous les résultats sont affichés.'
            )
          }
        }
        return null
      })
      .catch(() => setUser(null))
      .finally(() => {
        setIsLoading(false)
        if (LOGS_DATA) {
          apiAdage.logCatalogView({
            iframeFrom: removeParamsFromUrl(location.pathname),
            source: siret || venueId ? 'partnersMap' : 'homepage',
          })
        }
      })
  }, [])

  const removeVenueFilter = useCallback(() => setVenueFilter(null), [])

  const uniqueId = useId()
  useEffect(() => {
    // User token can not contains special characters
    initAlgoliaAnalytics(uniqueId.replace(/[\W_]/g, '_'))
  }, [])

  if (isLoading) {
    return <LoaderPage />
  }

  if (!user) {
    return <UnauthenticatedError />
  }

  return (
    <AdageUserContextProvider adageUser={user}>
      <FiltersContextProvider venueFilter={venueFilter}>
        <FacetFiltersContextProvider uai={user?.uai} venueFilter={venueFilter}>
          {user?.role &&
          [AdageFrontRoles.READONLY, AdageFrontRoles.REDACTOR].includes(
            user.role
          ) ? (
            <AppLayout
              removeVenueFilter={removeVenueFilter}
              venueFilter={venueFilter}
            />
          ) : (
            <UnauthenticatedError />
          )}
        </FacetFiltersContextProvider>
      </FiltersContextProvider>
    </AdageUserContextProvider>
  )
}
