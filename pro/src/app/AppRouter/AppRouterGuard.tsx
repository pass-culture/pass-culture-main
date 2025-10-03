import type { ReactNode } from 'react'
import { useSelector } from 'react-redux'
import { Navigate, Outlet, useLocation } from 'react-router'

import { findCurrentRoute } from '@/app/AppRouter/findCurrentRoute'
import {
  selectCurrentOffererIsOnboarded,
  selectOffererNames,
} from '@/commons/store/offerer/selectors'
import { selectCurrentUser } from '@/commons/store/user/selectors'

type AppRouterGuardProps = {
  children?: ReactNode
  onboardingOnly?: boolean
  unattachedOnly?: boolean
  publicOnly?: boolean
}
export const AppRouterGuard = ({ children }: AppRouterGuardProps) => {
  const location = useLocation()
  const currentRoute = findCurrentRoute(location)
  const currentUser = useSelector(selectCurrentUser)
  const offererNames = useSelector(selectOffererNames)
  const isUnAttached = useSelector((store: any) => store.user.isUnAttached)
  const currentOffererOnboarded = useSelector(selectCurrentOffererIsOnboarded)

  if (currentRoute) {
    if (!currentUser && !currentRoute?.meta?.public) {
      const fromUrl = encodeURIComponent(
        `${location.pathname}${location.search}`
      )

      const loginUrl =
        location.pathname === '/' ? '/connexion' : `/connexion?de=${fromUrl}`

      return <Navigate to={loginUrl} replace />
    } else if (
      currentUser &&
      !offererNames &&
      !location.pathname.startsWith('/inscription')
    ) {
      return <Navigate to="/inscription/structure/recherche" replace />
    } else if (
      isUnAttached !== null &&
      !isUnAttached &&
      !currentRoute?.meta?.unattachedOnly
    ) {
      return <Navigate to="/rattachement-en-cours" replace />
    } else if (
      currentOffererOnboarded !== null &&
      !currentOffererOnboarded &&
      !currentRoute?.meta?.onboardingOnly
    ) {
      return <Navigate to="/onboarding" replace />
    } else {
      return children ? children : <Outlet />
    }
  } else {
    return children ? children : <Outlet />
  }
}
