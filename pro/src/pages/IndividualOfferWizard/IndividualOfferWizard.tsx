/* istanbul ignore file */
import { Outlet, RouteObject, useLocation } from 'react-router-dom'

import { Layout } from 'app/App/layout/Layout'
import { IndividualOfferContextProvider } from 'commons/context/IndividualOfferContext/IndividualOfferContext'

import styles from './IndividualOfferWizard.module.scss'

export const IndividualOfferWizard = () => {
  const { pathname } = useLocation()
  const isOnboarding = pathname.indexOf('onboarding') !== -1
  const isConfirmationPage = pathname.endsWith('confirmation')

  return (
    <Layout
      layout={
        isOnboarding
          ? 'sticky-onboarding'
          : isConfirmationPage
            ? 'basic'
            : 'sticky-actions'
      }
    >
      <IndividualOfferContextProvider>
        <div className={styles['offer-wizard-container']}>
          <Outlet />
        </div>
      </IndividualOfferContextProvider>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component: RouteObject['Component'] = IndividualOfferWizard
