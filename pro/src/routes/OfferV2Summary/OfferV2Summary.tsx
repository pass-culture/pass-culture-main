import React from 'react'
import { useLocation, useParams } from 'react-router-dom'

import { OfferIndividualContextProvider } from 'context/OfferIndividualContext'
import useActiveFeature from 'hooks/useActiveFeature'
import useCurrentUser from 'hooks/useCurrentUser'
import { Summary } from 'routes/OfferIndividualWizard/Summary'
import { parse } from 'utils/query-string'

const OfferV2Summary = (): JSX.Element | null => {
  const { currentUser } = useCurrentUser()
  const { offerId } = useParams<{ offerId: string }>()
  const { search } = useLocation()
  const { structure: offererId } = parse(search)
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')

  return (
    <OfferIndividualContextProvider
      isUserAdmin={currentUser.isAdmin}
      offerId={offerId}
      queryOffererId={offererId}
    >
      <Summary isOfferV2={!isOfferFormV3} />
    </OfferIndividualContextProvider>
  )
}

export default OfferV2Summary
