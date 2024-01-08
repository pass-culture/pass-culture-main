import { useLocation, useParams, Outlet, RouteObject } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { IndividualOfferContextProvider } from 'context/IndividualOfferContext'
import { getIndividualOfferAdapter } from 'core/Offers/adapters'
import { IndividualOffer } from 'core/Offers/types'
import useCurrentUser from 'hooks/useCurrentUser'
import { parse } from 'utils/query-string'

const IndividualOfferWizard = () => {
  const { currentUser } = useCurrentUser()
  const { offerId } = useParams<{ offerId: string }>()
  const { search } = useLocation()
  const { structure: offererId, 'sous-categorie': querySubcategoryId } =
    parse(search)
  return (
    <AppLayout>
      <IndividualOfferContextProvider
        isUserAdmin={currentUser.isAdmin}
        offerId={offerId === 'creation' ? undefined : offerId}
        queryOffererId={offererId}
        querySubcategoryId={querySubcategoryId}
      >
        <Outlet />
      </IndividualOfferContextProvider>
    </AppLayout>
  )
}

// Lazy-loaded by react-router-dom
// ts-unused-exports:disable-next-line
export const Component: RouteObject['Component'] = IndividualOfferWizard

export type IndividualOfferWizardLoaderData = { offer: IndividualOffer | null }

// ts-unused-exports:disable-next-line
export const loader: RouteObject['loader'] = async ({
  params,
}): Promise<IndividualOfferWizardLoaderData> => {
  if (params.offerId === 'creation') {
    return {
      offer: null,
    }
  }

  const response = await getIndividualOfferAdapter(Number(params.offerId))
  return {
    offer: response.payload,
  }
}

// Used to manually retrigger loader
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
