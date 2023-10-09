import React from 'react'
import { useLocation } from 'react-router-dom'

import { BannerCreateOfferAdmin } from 'components/Banner'
import { useIndividualOfferContext } from 'context/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { useOfferWizardMode } from 'hooks'
import useCurrentUser from 'hooks/useCurrentUser'
import IndividualOfferLayout from 'screens/IndividualOffer/IndividualOfferLayout/IndividualOfferLayout'
import { getTitle } from 'screens/IndividualOffer/IndividualOfferLayout/utils/getTitle'
import InformationsScreen from 'screens/IndividualOffer/InformationsScreen/InformationsScreen'
import { parse } from 'utils/query-string'

const Offer = (): JSX.Element | null => {
  const mode = useOfferWizardMode()
  const { currentUser } = useCurrentUser()
  const { offer, setOffer } = useIndividualOfferContext()

  const { search } = useLocation()
  const { structure: offererId, lieu: venueId } = parse(search)

  const showAdminCreationBanner =
    currentUser.isAdmin &&
    mode === OFFER_WIZARD_MODE.CREATION &&
    !(offererId || offer)

  return (
    <IndividualOfferLayout
      offer={offer}
      setOffer={setOffer}
      title={getTitle(mode)}
      mode={mode}
    >
      {showAdminCreationBanner ? (
        <BannerCreateOfferAdmin />
      ) : (
        <InformationsScreen offererId={offererId} venueId={venueId} />
      )}
    </IndividualOfferLayout>
  )
}

export default Offer
