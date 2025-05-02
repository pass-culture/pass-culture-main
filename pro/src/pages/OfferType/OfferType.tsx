import { useSelector } from 'react-redux'
import { useLocation, Navigate } from 'react-router'

import { Layout } from 'app/App/layout/Layout'
import { useOfferer } from 'commons/hooks/swr/useOfferer'
import { useHasAccessToDidacticOnboarding } from 'commons/hooks/useHasAccessToDidacticOnboarding'
import { selectCurrentOffererId } from 'commons/store/offerer/selectors'
import { CollectiveBudgetCallout } from 'components/CollectiveBudgetInformation/CollectiveBudgetCallout'

import { OfferTypeScreen } from './OfferType/OfferType'

export const OfferType = (): JSX.Element => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const isDidacticOnboardingEnabled = useHasAccessToDidacticOnboarding()

  const queryOffererId = useSelector(selectCurrentOffererId)?.toString()
  const { data: offerer } = useOfferer(queryOffererId)

  if (isOnboarding && isDidacticOnboardingEnabled === false) {
    return <Navigate to="/accueil" />
  }

  return (
    <Layout
      mainHeading="Créer une offre"
      mainTopElement={
        !isOnboarding &&
        offerer?.allowedOnAdage && (
          <CollectiveBudgetCallout pageName="offer-creation-hub" />
        )
      }
      layout={isOnboarding ? 'sticky-onboarding' : 'sticky-actions'}
    >
      <OfferTypeScreen />
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OfferType
