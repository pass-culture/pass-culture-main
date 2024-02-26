import React from 'react'

import { ListOffersVenueResponseModel } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'

import CheckboxCell from './Cells/CheckboxCell'
import IndividualActionsCells from './Cells/IndividualActionsCells'
import OfferNameCell from './Cells/OfferNameCell'
import OfferRemainingStockCell from './Cells/OfferRemainingStockCell'
import OfferStatusCell from './Cells/OfferStatusCell'
import OfferVenueCell from './Cells/OfferVenueCell'
import ThumbCell from './Cells/ThumbCell'

type IndividualOfferItemProps = {
  disabled: boolean
  isSelected: boolean
  offer: Offer
  selectOffer: (offerId: number, selected: boolean, isTemplate: boolean) => void
  editionOfferLink: string
  editionStockLink: string
  venue: ListOffersVenueResponseModel
  isOfferEditable: boolean
  refreshOffers: () => void
  audience: Audience
}

const IndividualOfferItem = ({
  disabled,
  offer,
  isSelected,
  selectOffer,
  editionOfferLink,
  editionStockLink,
  venue,
  isOfferEditable,
  refreshOffers,
  audience,
}: IndividualOfferItemProps) => {
  return (
    <>
      <CheckboxCell
        offerName={offer.name}
        offerId={offer.id}
        status={offer.status}
        disabled={disabled}
        isSelected={isSelected}
        selectOffer={selectOffer}
        isShowcase={Boolean(offer.isShowcase)}
      />

      <ThumbCell offer={offer} editionOfferLink={editionOfferLink} />

      <OfferNameCell
        offer={offer}
        editionOfferLink={editionOfferLink}
        audience={audience}
      />

      <OfferVenueCell venue={venue} />

      <OfferRemainingStockCell stocks={offer.stocks} />

      <OfferStatusCell status={offer.status} />

      <IndividualActionsCells
        offer={offer}
        isOfferEditable={isOfferEditable}
        editionOfferLink={editionOfferLink}
        editionStockLink={editionStockLink}
        refreshOffers={refreshOffers}
      />
    </>
  )
}

export default IndividualOfferItem
