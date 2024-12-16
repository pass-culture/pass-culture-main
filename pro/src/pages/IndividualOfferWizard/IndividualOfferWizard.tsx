/* istanbul ignore file */
import { Outlet, RouteObject, useLocation } from 'react-router'

import { Layout } from 'app/App/layout/Layout'
import { IndividualOfferContextProvider } from 'commons/context/IndividualOfferContext/IndividualOfferContext'

const IndividualOfferWizard = () => {
  const { pathname } = useLocation()

  const isConfirmationPage = pathname.endsWith('confirmation')

  return (
    <Layout layout={isConfirmationPage ? 'basic' : 'sticky-actions'}>
      <IndividualOfferContextProvider>
        <Outlet />
      </IndividualOfferContextProvider>
    </Layout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component: RouteObject['Component'] = IndividualOfferWizard
