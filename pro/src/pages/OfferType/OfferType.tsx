import { useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { useIsAllowedOnAdage } from '@/commons/hooks/useIsAllowedOnAdage'
import { CollectiveBudgetCallout } from '@/components/CollectiveBudgetInformation/CollectiveBudgetCallout'

import { OfferTypeScreen } from './OfferType/OfferType'

export const OfferType = (): JSX.Element => {
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const collectiveOnly = queryParams.get('type') === 'collective'

  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const allowedOnAdage = useIsAllowedOnAdage()

  const mainHeading = `Créer une offre${collectiveOnly ? ' collective' : ''}`
  const children = <OfferTypeScreen collectiveOnly={collectiveOnly} />

  return isOnboarding ? (
    <OnboardingLayout
      mainHeading={mainHeading}
      isStickyActionBarInChild
      isEntryScreen
    >
      {children}
    </OnboardingLayout>
  ) : (
    <BasicLayout mainHeading={mainHeading} isStickyActionBarInChild>
      {allowedOnAdage && (
        <CollectiveBudgetCallout pageName="offer-creation-hub" />
      )}
      {children}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OfferType
