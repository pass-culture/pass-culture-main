import React from 'react'

import { Offer, Venue } from 'core/Offers/types'

import CheckboxCell from './Cells/CheckboxCell'
import EditOfferCell from './Cells/EditOfferCell'
import EditStocksCell from './Cells/EditStocksCell'
import OfferNameCell from './Cells/OfferNameCell'
import OfferRemainingStockCell from './Cells/OfferRemainingStockCell'
import OfferStatusCell from './Cells/OfferStatusCell'
import OfferVenueCell from './Cells/OfferVenueCell'
import ThumbCell from './Cells/ThumbCell'

export type IndividualOfferItemProps = {
  disabled: boolean
  isSelected: boolean
  offer: Offer
  selectOffer: (offerId: string, selected: boolean, isTemplate: boolean) => void
  editionOfferLink: string
  editionStockLink: string
  venue: Venue
  isOfferEditable: boolean
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
}: IndividualOfferItemProps) => {
  return (
    <>
      <CheckboxCell
        offerId={offer.id}
        status={offer.status}
        disabled={disabled}
        isSelected={isSelected}
        selectOffer={selectOffer}
        isShowcase={Boolean(offer.isShowcase)}
      />
      <ThumbCell offer={offer} editionOfferLink={editionOfferLink} />
      <OfferNameCell offer={offer} editionOfferLink={editionOfferLink} />
      <OfferVenueCell venue={venue} />
      <OfferRemainingStockCell stocks={offer.stocks} />
      <OfferStatusCell status={offer.status} />
      <EditStocksCell editionStockLink={editionStockLink} />
      <EditOfferCell
        isOfferEditable={isOfferEditable}
        name={offer.name}
        editionOfferLink={editionOfferLink}
      />
    </>
  )
}

export default IndividualOfferItem
