import { setUser as setSentryUser } from '@sentry/browser'
import { useEffect, useState } from 'react'
import useSWRMutation from 'swr/mutation'

import {
  AdageFrontRoles,
  type AuthenticatedResponse,
  type CatalogViewBody,
} from '@/apiClient/adage'
import { apiAdage } from '@/apiClient/api'
import { LOG_CATALOG_VIEW_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { LOGS_DATA } from '@/commons/utils/config'
import { AppLayout } from '@/pages/AdageIframe/app/components/AppLayout/AppLayout'

import { LoaderPage } from './components/LoaderPage/LoaderPage'
import { UnauthenticatedError } from './components/UnauthenticatedError/UnauthenticatedError'
import { AdageUserContextProvider } from './providers/AdageUserContext'

export const App = (): JSX.Element => {
  const [user, setUser] = useState<AuthenticatedResponse | null>()
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const params = new URLSearchParams(window.location.search)
  const siret = params.get('siret')
  const venueId = Number(params.get('venue'))

  const { trigger: logCatalogView } = useSWRMutation(
    LOG_CATALOG_VIEW_QUERY_KEY,
    (
      _key: string,
      options: {
        arg: CatalogViewBody
      }
    ) => apiAdage.logCatalogView({ body: options.arg })
  )

  useEffect(() => {
    const logData = () => {
      if (LOGS_DATA) {
        logCatalogView({
          iframeFrom: location.pathname,
          source: siret || venueId ? 'partnersMap' : 'homepage',
        })
      }
    }

    async function authenticate() {
      setIsLoading(true)
      try {
        const user = await apiAdage.authenticate()
        setUser(user)
        if (user.email) {
          setSentryUser({ email: user.email })
        }
        logData()
      } catch {
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    authenticate()
  }, [siret, venueId, logCatalogView])

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
