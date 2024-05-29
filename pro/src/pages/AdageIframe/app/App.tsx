import { setUser as setSentryUser } from '@sentry/browser'
import { useEffect, useId, useState } from 'react'
import useSWRMutation from 'swr/mutation'

import {
  AdageFrontRoles,
  AuthenticatedResponse,
  CatalogViewBody,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import { LOG_CATALOG_VIEW_QUERY_KEY } from 'config/swrQueryKeys'
import { useNotification } from 'hooks/useNotification'
import { LOGS_DATA } from 'utils/config'

import { initAlgoliaAnalytics } from '../libs/initAlgoliaAnalytics'

import { AppLayout } from './components/AppLayout/AppLayout'
import { LoaderPage } from './components/LoaderPage/LoaderPage'
import { UnauthenticatedError } from './components/UnauthenticatedError/UnauthenticatedError'
import { AdageUserContextProvider } from './providers/AdageUserContext'

export const App = (): JSX.Element => {
  const [user, setUser] = useState<AuthenticatedResponse | null>()
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const notification = useNotification()
  const uniqueId = useId()

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
    ) => apiAdage.logCatalogView(options.arg)
  )

  useEffect(() => {
    async function authenticate() {
      setIsLoading(true)
      try {
        const user = await apiAdage.authenticate()
        setUser(user)
        user.email && setSentryUser({ email: user.email })
      } catch {
        setUser(null)
      } finally {
        setIsLoading(false)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    authenticate()

    if (LOGS_DATA) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises
      logCatalogView({
        iframeFrom: location.pathname,
        source: siret || venueId ? 'partnersMap' : 'homepage',
      })
    }
  }, [notification, siret, venueId])

  useEffect(() => {
    // User token can not contains special characters
    initAlgoliaAnalytics(uniqueId.replace(/[\W_]/g, '_'))
  }, [uniqueId])

  if (isLoading) {
    return <LoaderPage />
  }

  if (!user) {
    return <UnauthenticatedError />
  }

  return (
    <AdageUserContextProvider adageUser={user}>
      {user.role &&
      [AdageFrontRoles.READONLY, AdageFrontRoles.REDACTOR].includes(
        user.role
      ) ? (
        <AppLayout />
      ) : (
        <UnauthenticatedError />
      )}
    </AdageUserContextProvider>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = App
