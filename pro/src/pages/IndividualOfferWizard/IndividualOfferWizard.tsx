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

export const IndividualOfferWizard = () => {
  const mode = useOfferWizardMode()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const isConfirmationPage = pathname.endsWith('confirmation')
  const { offer } = useIndividualOfferContext()
  const mainHeading = getTitle(mode, offer?.name ?? '')

  console.log({ mainHeading })

  const children = (
    <div className={styles['offer-wizard-container']}>
      <Outlet />
    </div>
  )

  return isOnboarding ? (
    <OnboardingLayout mainHeading={mainHeading} isStickyActionBarInChild>
      {children}
    </OnboardingLayout>
  ) : (
    <BasicLayout
      mainHeading={mainHeading}
      isStickyActionBarInChild={!isConfirmationPage}
    >
      {children}
    </BasicLayout>
  )
}

export const IndividualOfferWizardWrapper = () => {
  return (
    <IndividualOfferContextProvider>
      <IndividualOfferWizard />
    </IndividualOfferContextProvider>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferWizardWrapper
