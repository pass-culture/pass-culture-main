import React from 'react'
import { useLocation } from 'react-router-dom'

import { BannerCreateOfferAdmin } from 'components/Banner'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useOfferWizardMode } from 'hooks'
import useCurrentUser from 'hooks/useCurrentUser'
import IndivualOfferLayout from 'screens/IndividualOffer/IndivualOfferLayout/IndivualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndivualOfferLayout/utils/getTitle'
import InformationsScreen from 'screens/IndividualOffer/InformationsScreen/InformationsScreen'
import { parse } from 'utils/query-string'

export const Offer = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { currentUser } = useCurrentUser()
  const { offer } = useIndividualOfferContext()

  const { search } = useLocation()
  const { structure: offererId, lieu: venueId } = parse(search)

  const showAdminCreationBanner =
    currentUser.isAdmin &&
    mode === OFFER_WIZARD_MODE.CREATION &&
    !(offererId || offer)

  return (
    <IndivualOfferLayout offer={offer} title={getTitle(mode)} mode={mode}>
      {showAdminCreationBanner ? (
        <BannerCreateOfferAdmin />
      ) : (
        <InformationsScreen offererId={offererId} venueId={venueId} />
      )}
    </IndivualOfferLayout>
  )
}

// Below exports are used by react-router-dom
// ts-unused-exports:disable-next-line
export const Component = Offer
