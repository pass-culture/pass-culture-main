import { useEffect } from 'react'
import { useSelector } from 'react-redux'
import { useLocation } from 'react-router'

import { findCurrentRoute } from '@/app/AppRouter/findCurrentRoute'
import { selectCurrentUser } from '@/commons/store/user/selectors'

export const useFocus = (): void => {
  const location = useLocation()

  const currentRoute = findCurrentRoute(location)
  const isErrorPage = currentRoute?.isErrorPage

  const currentUser = useSelector(selectCurrentUser)
  const isConnected = !!currentUser

  useEffect(() => {
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
      // Fallback : if this doesnt work, focus will be document.activeElement = body.
      goToContent.focus()
    }
  }, [location.pathname])
}
