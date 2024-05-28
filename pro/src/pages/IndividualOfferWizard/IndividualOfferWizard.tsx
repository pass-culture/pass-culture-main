/* istanbul ignore file */
import { Outlet, RouteObject } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { IndividualOfferContextProvider } from 'context/IndividualOfferContext/IndividualOfferContext'

const IndividualOfferWizard = () => {
  return (
    <AppLayout layout={'sticky-actions'}>
      <IndividualOfferContextProvider>
        <Outlet />
      </IndividualOfferContextProvider>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component: RouteObject['Component'] = IndividualOfferWizard
