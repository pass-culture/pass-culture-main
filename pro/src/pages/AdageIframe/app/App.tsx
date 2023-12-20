import * as React from 'react'
import { useEffect, useId, useState } from 'react'

import { AdageFrontRoles, AuthenticatedResponse } from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import useNotification from 'hooks/useNotification'
import { LOGS_DATA } from 'utils/config'

import { initAlgoliaAnalytics } from '../libs/initAlgoliaAnalytics'

import { AppLayout } from './components/AppLayout/AppLayout'
import { LoaderPage } from './components/LoaderPage/LoaderPage'
import { UnauthenticatedError } from './components/UnauthenticatedError/UnauthenticatedError'
import { AdageUserContextProvider } from './providers/AdageUserContext'

export const App = (): JSX.Element => {
  const params = new URLSearchParams(window.location.search)
  const [user, setUser] = useState<AuthenticatedResponse | null>()
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const { error } = useNotification()
  const siret = params.get('siret')
  const venueId = Number(params.get('venue'))

  useEffect(() => {
    async function authenticate() {
      setIsLoading(true)
      try {
        const user = await apiAdage.authenticate()
        setUser(user)
      } catch {
        setUser(null)
      } finally {
        setIsLoading(false)
      }

      if (LOGS_DATA) {
        // eslint-disable-next-line @typescript-eslint/no-floating-promises
        apiAdage.logCatalogView({
          iframeFrom: location.pathname,
          source: siret || venueId ? 'partnersMap' : 'homepage',
        })
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    authenticate()
  }, [error, siret, venueId])

  const uniqueId = useId()
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
      {user?.role &&
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
