import OfferItem from '../OfferItem/OfferItem'
import React from 'react'

type OffersTableBodyProps = {
  areAllOffersSelected: boolean
  offers: any[]
  selectOffer: (offerId: string) => void
  selectedOfferIds: string[]
  isNewModelEnabled: boolean
  enableIndividualAndCollectiveSeparation: boolean
}
const OffersTableBody = ({
  areAllOffersSelected,
  offers,
  selectOffer,
  selectedOfferIds,
  isNewModelEnabled,
  enableIndividualAndCollectiveSeparation,
}: OffersTableBodyProps) => (
  <tbody className="offers-list">
    {offers.map(offer => {
      let offerId = ''

      if (isNewModelEnabled) {
        offerId = `${offer.isShowcase ? `T-` : ''}${offer.id}`
      } else if (
        !isNewModelEnabled &&
        enableIndividualAndCollectiveSeparation
      ) {
        offerId = offer.offerId
      } else {
        offerId = offer.id
      }

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
