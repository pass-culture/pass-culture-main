import React from 'react'

import { Audience } from 'core/shared'

import OfferItem from '../OfferItem/OfferItem'

type OffersTableBodyProps = {
  areAllOffersSelected: boolean
  offers: any[]
  selectOffer: (
    offerId: string,
    isSelected: boolean,
    isTemplate: boolean
  ) => void
  selectedOfferIds: string[]
  audience: Audience
}

const OffersTableBody = ({
  areAllOffersSelected,
  offers,
  selectOffer,
  selectedOfferIds,
  audience,
}: OffersTableBodyProps) => (
  <tbody className="offers-list">
    {offers.map(offer => {
      const offerId = `${offer.isShowcase ? `T-` : ''}${offer.id}`

      return (
        <OfferItem
          disabled={areAllOffersSelected}
          isSelected={selectedOfferIds.includes(offerId)}
          key={offerId}
          offer={offer}
          selectOffer={selectOffer}
          audience={audience}
        />
      )
    })}
  </tbody>
)

export default OffersTableBody
