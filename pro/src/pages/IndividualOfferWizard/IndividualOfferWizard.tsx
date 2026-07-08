/* istanbul ignore file */

import { Outlet, useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { HeadlineOfferContextProvider } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { IndividualOfferContextProvider } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'

import styles from './IndividualOfferWizard.module.scss'

const IndividualOfferWizardConsumer = () => {
  const { pathname } = useLocation()

  const isOnboarding = pathname.includes('onboarding')
  const isConfirmationPage = pathname.endsWith('confirmation')

  const children = (
    <div className={styles['offer-wizard-container']}>
      <Outlet />
    </div>
  )

  if (isOnboarding) {
    return (
      <OnboardingLayout isStickyActionBarInChild>{children}</OnboardingLayout>
    )
  }

  return (
    <BasicLayout isStickyActionBarInChild={!isConfirmationPage}>
      {children}
    </BasicLayout>
  )
}

export const IndividualOfferWizard = () => {
  return (
    <IndividualOfferContextProvider>
      <HeadlineOfferContextProvider>
        <IndividualOfferWizardConsumer />
      </HeadlineOfferContextProvider>
    </IndividualOfferContextProvider>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferWizard
