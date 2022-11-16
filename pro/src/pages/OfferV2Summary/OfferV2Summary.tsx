import React from 'react'
import { useLocation, useParams } from 'react-router-dom'

import { OfferIndividualContextProvider } from 'context/OfferIndividualContext'
import useCurrentUser from 'hooks/useCurrentUser'
import { Summary } from 'pages/OfferIndividualWizard/Summary'
import { parse } from 'utils/query-string'

const OfferV2Summary = (): JSX.Element | null => {
  const { currentUser } = useCurrentUser()
  const { offerId } = useParams<{ offerId: string }>()
  const { search } = useLocation()
  const { structure: offererId } = parse(search)

  return (
    <OfferIndividualContextProvider
      isUserAdmin={currentUser.isAdmin}
      offerId={offerId}
      queryOffererId={offererId}
    >
      <Summary isOfferV2 />
    </OfferIndividualContextProvider>
  )
}

export default OfferV2Summary
