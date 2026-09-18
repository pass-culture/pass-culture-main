import { useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { Title } from '@/ui-kit/Title/Title'

import { OfferTypeScreen } from './OfferType/OfferType'

export const OfferType = (): JSX.Element => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')

  const children = <OfferTypeScreen />

  return isOnboarding ? (
    <OnboardingLayout isStickyActionBarInChild isEntryScreen>
      <Title level="1" title="Créer une offre collective" marginBottom="xxl" />
      {children}
    </OnboardingLayout>
  ) : (
    <BasicLayout isStickyActionBarInChild>
      <Title level="1" title="Créer une offre collective" marginBottom="xxl" />
      {children}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OfferType
