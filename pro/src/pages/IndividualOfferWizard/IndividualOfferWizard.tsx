import React from 'react'
import { useLocation, useParams, Outlet } from 'react-router-dom'

import { AppLayout } from 'app/AppLayout'
import { IndividualOfferContextProvider } from 'context/IndividualOfferContext'
import useCurrentUser from 'hooks/useCurrentUser'
import { parse } from 'utils/query-string'

export const IndividualOfferWizard = () => {
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
export const Component = IndividualOfferWizard
