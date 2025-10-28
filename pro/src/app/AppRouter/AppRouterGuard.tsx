import { memo, type ReactNode } from 'react'
import { useSelector } from 'react-redux'
import { Navigate, useLocation, useSearchParams } from 'react-router'

import { findCurrentRoute } from '@/app/AppRouter/findCurrentRoute'
import type { UserAccess } from '@/commons/store/user/reducer'

type AppRouterGuardProps = {
  children: ReactNode
  onboardingOnly?: boolean
  unattachedOnly?: boolean
  publicOnly?: boolean
}
export const AppRouterGuard = memo(({ children }: AppRouterGuardProps) => {
  const location = useLocation()
  const [searchParams] = useSearchParams()
  const currentRoute = findCurrentRoute(location)
  const userAccess: UserAccess = useSelector((store: any) => store.user.access)

  if (currentRoute) {
    if (!userAccess && !currentRoute?.meta?.public) {
      const fromUrl = encodeURIComponent(
        `${location.pathname}${location.search}`
      )

      const loginUrl =
        location.pathname === '/' ? '/connexion' : `/connexion?de=${fromUrl}`

      return <Navigate to={loginUrl} replace />
    } else if (
      userAccess &&
      !currentRoute?.meta?.canBeLoggedIn &&
      currentRoute?.meta?.public
    ) {
      const redirectUrl =
        searchParams.get('de') ??
        (searchParams ? `/accueil?${searchParams}` : '/accueil')

      return <Navigate to={redirectUrl ?? '/accueil'} replace />
    } else if (
      userAccess === 'no-offerer' &&
      !location.pathname.startsWith('/inscription')
    ) {
      return <Navigate to="/inscription/structure/recherche" replace />
    } else if (
      userAccess === 'unattached' &&
      !currentRoute?.meta?.unattachedOnly &&
      !currentRoute?.meta?.canBeUnattached
    ) {
      return <Navigate to="/rattachement-en-cours" replace />
    } else if (
      userAccess === 'no-onboarding' &&
      !currentRoute?.meta?.onboardingOnly &&
      !currentRoute?.meta?.canBeOnboarding
    ) {
      return <Navigate to="/onboarding" replace />
    } else if (
      userAccess === 'full' &&
      (currentRoute?.meta?.onboardingOnly || currentRoute?.meta?.unattachedOnly)
    ) {
      return <Navigate to="/accueil" replace />
    } else {
      return children
    }
  } else {
    return children
  }
})
