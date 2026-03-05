/* istanbul ignore file */

import { Outlet, useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import {
  IndividualOfferContextProvider,
  useIndividualOfferContext,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'

import styles from './IndividualOfferWizard.module.scss'
import { getTitle } from './utils/getTitle'

const IndividualOfferWizardConsumer = () => {
  const { offer } = useIndividualOfferContext()
  const mode = useOfferWizardMode()
  const { pathname } = useLocation()

  const isOnboarding = pathname.includes('onboarding')
  const isConfirmationPage = pathname.endsWith('confirmation')

  const mainHeading = getTitle(mode, isConfirmationPage, offer?.name)

  const children = (
    <div className={styles['offer-wizard-container']}>
      <Outlet />
    </div>
  )

  if (isOnboarding) {
    return (
      <OnboardingLayout mainHeading={mainHeading} isStickyActionBarInChild>
        {children}
      </OnboardingLayout>
    )
  }

  return (
    <BasicLayout
      mainHeading={mainHeading}
      isStickyActionBarInChild={!isConfirmationPage}
      isHeadingCentered={isConfirmationPage}
    >
      {children}
    </BasicLayout>
  )
}

export const IndividualOfferWizard = () => {
  return (
    <IndividualOfferContextProvider>
      <IndividualOfferWizardConsumer />
    </IndividualOfferContextProvider>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferWizard
