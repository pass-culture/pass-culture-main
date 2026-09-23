import { setUser } from '@sentry/browser'
import type { JSX } from 'react'
import { useLocation, useSearchParams } from 'react-router'
import useSWR from 'swr'
import useSWRMutation from 'swr/mutation'

import { AdageFrontRoles, type CatalogViewBody } from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import {
  GET_AUTHENTICATED_ADAGE_USER,
  LOG_CATALOG_VIEW_QUERY_KEY,
} from '@/commons/config/swrQueryKeys'
import { LOGS_DATA } from '@/commons/utils/config'
import { AppLayout } from '@/pages/AdageIframe/app/components/AppLayout/AppLayout'

import { LoaderPage } from './components/LoaderPage/LoaderPage'
import { UnauthenticatedError } from './components/UnauthenticatedError/UnauthenticatedError'
import { AdageUserContextProvider } from './providers/AdageUserContext'

export const App = (): JSX.Element => {
  const [searchParams] = useSearchParams()
  const location = useLocation()
  const siret = searchParams.get('siret')
  const venueId = Number(searchParams.get('venue'))

  const { trigger: logCatalogView } = useSWRMutation(
    LOG_CATALOG_VIEW_QUERY_KEY,
    (
      _key: string,
      options: {
        arg: CatalogViewBody
      }
    ) => apiAdage.logCatalogView({ body: options.arg })
  )

  const { data: user, isLoading } = useSWR([GET_AUTHENTICATED_ADAGE_USER], () =>
    apiAdage.authenticate()
  )

  if (user?.email) {
    setUser({ email: user.email })
  }

  if (LOGS_DATA && user && (venueId || siret)) {
    logCatalogView({
      iframeFrom: location.pathname,
      source: siret || venueId ? 'partnersMap' : 'homepage',
    })
  }

  if (isLoading) {
    return <LoaderPage />
  }

  if (!user) {
    return <UnauthenticatedError />
  }

  return (
    <AdageUserContextProvider adageUser={user}>
      {[AdageFrontRoles.READONLY, AdageFrontRoles.REDACTOR].includes(
        user.role
      ) ? (
        <AppLayout />
      ) : (
        <UnauthenticatedError />
      )}
    </AdageUserContextProvider>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = App
