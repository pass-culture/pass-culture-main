import React from 'react'

import { legacyComputeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { Offer } from 'core/Offers/types'
import { Audience } from 'core/shared'

import OfferItem from '../OfferItem/OfferItem'

type OffersTableBodyProps = {
  areAllOffersSelected: boolean
  offers: Offer[]
  selectOffer: (
    offerId: string,
    isSelected: boolean,
    isTemplate: boolean
  ) => void
  selectedOfferIds: string[]
  audience: Audience
  refreshOffers: () => void
}

const OffersTableBody = ({
  areAllOffersSelected,
  offers,
  selectOffer,
  selectedOfferIds,
  audience,
  refreshOffers,
}: OffersTableBodyProps) => (
  <tbody className="offers-list">
    {offers.map(offer => {
      const offerId = legacyComputeURLCollectiveOfferId(
        offer.id,
        Boolean(offer.isShowcase)
      )

      return (
        <OfferItem
          disabled={areAllOffersSelected}
          isSelected={selectedOfferIds.includes(offerId)}
          key={offerId}
          offer={offer}
          selectOffer={selectOffer}
          audience={audience}
          refreshOffers={refreshOffers}
        />
      )
    })}
  </tbody>
)

export default OffersTableBody
