import { useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'

import { OfferTypeScreen } from './OfferType/OfferType'

export const OfferType = (): JSX.Element => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1

  const children = <OfferTypeScreen />

  return isOnboarding ? (
    <OnboardingLayout
      mainHeading="Créer une offre collective"
      isStickyActionBarInChild
      isEntryScreen
    >
      {children}
    </OnboardingLayout>
  ) : (
    <BasicLayout
      mainHeading="Créer une offre collective"
      isStickyActionBarInChild
    >
      {children}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OfferType
