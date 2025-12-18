import { useEffect } from 'react'
import { useLocation } from 'react-router'

import { RouteId } from '@/app/AppRouter/constants'
import { findCurrentRoute } from '@/app/AppRouter/findCurrentRoute'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { selectCurrentUser } from '@/commons/store/user/selectors'

const EXCLUDED_ROUTES: Set<string> = new Set([RouteId.Hub])

/**
 * @deprecated Replaced by `useFocusOnMounted`.
 */
export const useFocus = (): void => {
  const location = useLocation()

  const currentRoute = findCurrentRoute(location)
  const isErrorPage = currentRoute?.isErrorPage

  const currentRouteId = currentRoute?.id
  const currentUser = useAppSelector(selectCurrentUser)
  const isConnected = !!currentUser
  const isExcludedRoute = currentRouteId && EXCLUDED_ROUTES.has(currentRouteId)

  useEffect(() => {
    // TODO (igabriele, 2025-12-17): This useEffect is a complex pattern to maintain, it will likely be replaced by a focus handling done within each page to clarify responsability.
    // In the meantime, we gradually exclude pages that migrated to `useFocusOnMounted`:
    if (isExcludedRoute) {
      return
    }

    /* istanbul ignore next : E2E tested */
    document.getElementById('content-wrapper')?.scrollTo(0, 0)

    if (isErrorPage) {
      const errorReturnLink = document.getElementById('error-return-link')
      if (errorReturnLink) {
        errorReturnLink.focus()
      }
      return
    }

    const backToNav = document.getElementById('back-to-nav-link')
    const goToContent = document.getElementById('go-to-content')
    // Mind that those are subject to race conditions since they might be rendered after
    // the userEffect is triggered.
    // TODO (asaez-pass, 2025-09-16): a more robust way to implement this needs to be discussed.
    const doesPageHaveStepper = document.querySelector('#stepper')
    const doesPageHaveTabs = document.querySelector('#tablist')

    if (isConnected) {
      if (doesPageHaveStepper) {
        // We don't want to focus the back to nav link if there is a stepper on the page,
        // but regain focus on active step (if any)
        // > check Stepper.tsx
        const activeStep = document.querySelector('#stepper #active a')
        if (activeStep) {
          ;(activeStep as HTMLElement).focus()
        }
      } else if (doesPageHaveTabs) {
        // We don't want to focus the back to nav link if there are tabs on the page,
        // but regain focus on active tab (if any)
        // > check NavLinkItems.tsx
        const activeTab = document.querySelector('#tablist #selected a')
        if (activeTab) {
          ;(activeTab as HTMLElement).focus()
        }
      } else if (backToNav) {
        backToNav.focus()
      } else if (goToContent) {
        goToContent.focus()
      }
    } else if (goToContent) {
      goToContent.focus()
    }

    // If none of above is called, focus will be document.activeElement = body.
  }, [isConnected, isErrorPage, isExcludedRoute])
}
