/* istanbul ignore file */
import { Navigate, Outlet, useLocation } from 'react-router'

import { Layout } from 'app/App/layout/Layout'
import { IndividualOfferContextProvider } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { useHasAccessToDidacticOnboarding } from 'commons/hooks/useHasAccessToDidacticOnboarding'

import styles from './IndividualOfferWizard.module.scss'

export const IndividualOfferWizard = () => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const isConfirmationPage = pathname.endsWith('confirmation')
  const isDidacticOnboardingEnabled = useHasAccessToDidacticOnboarding()

  if (isOnboarding && isDidacticOnboardingEnabled === false) {
    return <Navigate to="/accueil" />
  }

  return (
    <Layout
      layout={
        isOnboarding
          ? 'sticky-onboarding'
          : isConfirmationPage
            ? 'basic'
            : 'sticky-actions'
      }
      areMainHeadingAndBackToNavLinkInChild
    >
      <IndividualOfferContextProvider>
        <div className={styles['offer-wizard-container']}>
          <Outlet />
        </div>
      </IndividualOfferContextProvider>
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferWizard
