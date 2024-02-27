/* istanbul ignore file */
import { Outlet, RouteObject, useLocation, useParams } from 'react-router-dom'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { AppLayout } from 'app/AppLayout'
import { IndividualOfferContextProvider } from 'context/IndividualOfferContext'
import useCurrentUser from 'hooks/useCurrentUser'
import { parse } from 'utils/query-string'

const IndividualOfferWizard = () => {
  const { currentUser } = useCurrentUser()
  const { offerId } = useParams<{ offerId: string }>()
  const { search } = useLocation()
  const { structure: offererId } = parse(search)
  return (
    <AppLayout layout={'sticky-actions'}>
      <IndividualOfferContextProvider
        isUserAdmin={currentUser.isAdmin}
        offerId={offerId === 'creation' ? undefined : offerId}
        queryOffererId={offererId}
      >
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
