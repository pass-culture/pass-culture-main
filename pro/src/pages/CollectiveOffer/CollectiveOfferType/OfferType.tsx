import { useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'

import { OfferTypeScreen } from './OfferType/OfferType'
import styles from './OfferType/OfferType.module.scss'

export const OfferType = (): JSX.Element => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.includes('onboarding')

  const children = <OfferTypeScreen />

  return isOnboarding ? (
    <OnboardingLayout isStickyActionBarInChild isEntryScreen>
      <h1 className={styles['title']}>Créer une offre collective</h1>
      {children}
    </OnboardingLayout>
  ) : (
    <BasicLayout isStickyActionBarInChild>
      <h1 className={styles['title']}>Créer une offre collective</h1>
      {children}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = OfferType
