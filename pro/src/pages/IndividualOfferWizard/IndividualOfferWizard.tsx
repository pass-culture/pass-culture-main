/* istanbul ignore file */
import { Outlet, RouteObject } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
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

export type IndividualOfferWizardLoaderData = {
  offer: GetIndividualOfferResponseModel | null
}

// ts-unused-exports:disable-next-line
export const loader: RouteObject['loader'] = async ({
  params,
}): Promise<IndividualOfferWizardLoaderData> => {
  if (params.offerId === 'creation') {
    return {
      offer: null,
    }
  }

  const offer = await api.getOffer(Number(params.offerId))

  return {
    offer,
  }
}

// Used to manually retrigger loader (call it with fetcher.submit)
// ts-unused-exports:disable-next-line
export const action: RouteObject['action'] = () => null

// ts-unused-exports:disable-next-line
export const shouldRevalidate: RouteObject['shouldRevalidate'] = ({
  currentUrl,
  nextUrl,
  formAction,
}) => {
  // Allow revalidation by using actions
  if (formAction) {
    return true
  }

  // Do not reload offerId when GET params change, only when pathname changes
  return currentUrl.pathname !== nextUrl.pathname
}
