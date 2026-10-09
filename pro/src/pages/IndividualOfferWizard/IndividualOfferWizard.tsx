/* istanbul ignore file */

import { Outlet, useLocation } from 'react-router'

import { ContentLayout } from '@/app/App/layouts/ContentLayout/ContentLayout'
import { FullLayout } from '@/app/App/layouts/FullLayout/FullLayout'
import { HeadlineOfferContextProvider } from '@/commons/context/HeadlineOfferContext/HeadlineOfferContext'
import { IndividualOfferContextProvider } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'

import styles from './IndividualOfferWizard.module.scss'

const IndividualOfferWizardConsumer = () => {
  const { pathname } = useLocation()

  const isOnboarding = pathname.includes('onboarding')

  const LayoutComponent = isOnboarding ? FullLayout : ContentLayout

  return (
    <LayoutComponent>
      <div className={styles['offer-wizard-container']}>
        <Outlet />
      </div>
    </LayoutComponent>
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
