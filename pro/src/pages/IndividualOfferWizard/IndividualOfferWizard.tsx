/* istanbul ignore file */
import { Outlet, RouteObject, useLocation } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { IndividualOfferContextProvider } from 'context/IndividualOfferContext/IndividualOfferContext'

const IndividualOfferWizard = () => {
  const { pathname } = useLocation()

  const isConfirmationPage = pathname.endsWith('confirmation')

  return (
    <AppLayout layout={isConfirmationPage ? 'basic' : 'sticky-actions'}>
      <IndividualOfferContextProvider>
        <Outlet />
      </IndividualOfferContextProvider>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component: RouteObject['Component'] = IndividualOfferWizard
