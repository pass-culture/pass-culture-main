import OfferItem from '../OfferItem/OfferItem'
import React from 'react'

type OffersTableBodyProps = {
  areAllOffersSelected: boolean
  offers: any[]
  selectOffer: (
    offerId: string,
    isSelected: boolean,
    isTemplate: boolean
  ) => void
  selectedOfferIds: string[]
}

const OffersTableBody = ({
  areAllOffersSelected,
  offers,
  selectOffer,
  selectedOfferIds,
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
        />
      )
    })}
  </tbody>
)

export default OffersTableBody
