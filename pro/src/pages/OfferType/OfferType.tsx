import { useSelector } from 'react-redux'
import { Navigate, useLocation } from 'react-router'

import { Layout } from '@/app/App/layout/Layout'
import { useOfferer } from '@/commons/hooks/swr/useOfferer'
import { useHasAccessToDidacticOnboarding } from '@/commons/hooks/useHasAccessToDidacticOnboarding'
import { selectCurrentOffererId } from '@/commons/store/offerer/selectors'
import { CollectiveBudgetCallout } from '@/components/CollectiveBudgetInformation/CollectiveBudgetCallout'

import { OfferTypeScreen } from './OfferType/OfferType'

export const OfferType = (): JSX.Element => {
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const collectiveOnly = queryParams.get('type') === 'collective'

  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const isDidacticOnboardingEnabled = useHasAccessToDidacticOnboarding()

  const selectedOffererId = useSelector(selectCurrentOffererId)

  const { data: offerer } = useOfferer(selectedOffererId?.toString())

  if (isOnboarding && isDidacticOnboardingEnabled === false) {
    return <Navigate to="/accueil" />
  }

  return (
    <Layout
      mainHeading={`Créer une offre${collectiveOnly ? ' collective' : ''}`}
      mainTopElement={
        !isOnboarding &&
        offerer?.allowedOnAdage && (
          <CollectiveBudgetCallout pageName="offer-creation-hub" />
        )
      }
      layout={isOnboarding ? 'sticky-onboarding' : 'sticky-actions'}
    >
      <OfferTypeScreen collectiveOnly={collectiveOnly} />
    </Layout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OfferType
