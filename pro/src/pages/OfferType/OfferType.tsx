import { Navigate, useLocation } from 'react-router-dom'

import { Layout } from 'app/App/layout/Layout'
import { useHasAccessToDidacticOnboarding } from 'commons/hooks/useHasAccessToDidacticOnboarding'

import { OfferTypeScreen } from './OfferType/OfferType'

export const OfferType = (): JSX.Element => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const isDidacticOnboardingEnabled = useHasAccessToDidacticOnboarding()

  if (isOnboarding && isDidacticOnboardingEnabled === false) {
    return <Navigate to="/accueil" />
  }

  return (
    <Layout layout={isOnboarding ? 'sticky-onboarding' : 'sticky-actions'}>
      <OfferTypeScreen />
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = OfferType
