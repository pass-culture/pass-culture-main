import { memo, type ReactNode } from 'react'
import { Navigate, useLocation, useSearchParams } from 'react-router'

import { findCurrentRoute } from '@/app/AppRouter/findCurrentRoute'
import { useAppSelector } from '@/commons/hooks/useAppSelector'

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
  const userAccess = useAppSelector((store) => store.user.access)

  if (currentRoute) {
    if (!userAccess && !currentRoute?.meta?.public) {
      // The user is not logged in and tries to access a private page.
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
      // the user is logged in and tries to access a page like subscription or connexion
      const redirectUrl =
        searchParams.get('de') ??
        (searchParams ? `/accueil?${searchParams}` : '/accueil')

      return <Navigate to={redirectUrl ?? '/accueil'} replace />
    } else if (
      userAccess === 'no-offerer' &&
      !location.pathname.startsWith('/inscription')
    ) {
      // the user has no offerer and tries to do anything other than creating one
      return <Navigate to="/inscription/structure/recherche" replace />
    } else if (
      userAccess === 'unattached' &&
      !currentRoute?.meta?.unattachedOnly &&
      !currentRoute?.meta?.canBeUnattached
    ) {
      // the user is unattached and tries to access a page that requires an offerer
      return <Navigate to="/rattachement-en-cours" replace />
    } else if (
      userAccess === 'no-onboarding' &&
      !currentRoute?.meta?.onboardingOnly &&
      !currentRoute?.meta?.canBeOnboarding &&
      !location.pathname.startsWith('/inscription')
    ) {
      // the user is not onboarded and tries to access anything other than onboarding and offerer creation
      return <Navigate to="/onboarding" replace />
    } else if (
      userAccess === 'full' &&
      (currentRoute?.meta?.onboardingOnly || currentRoute?.meta?.unattachedOnly)
    ) {
      // the user has full access and tries to access onboarding or unattached pages
      return <Navigate to="/accueil" replace />
    } else {
      return children
    }
  } else {
    return children
  }
})
