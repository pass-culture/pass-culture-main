/* istanbul ignore file */

import { Outlet, useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { OnboardingLayout } from '@/app/App/layouts/funnels/OnboardingLayout/OnboardingLayout'
import { IndividualOfferContextProvider } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'

import styles from './IndividualOfferWizard.module.scss'
import { getTitle } from './utils/getTitle'

export const IndividualOfferWizard = () => {
  const mode = useOfferWizardMode()
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const isConfirmationPage = pathname.endsWith('confirmation')
  const mainHeading = getTitle(mode)

  const children = (
    <IndividualOfferContextProvider>
      <div className={styles['offer-wizard-container']}>
        <Outlet />
      </div>
    </IndividualOfferContextProvider>
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

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = IndividualOfferWizard
