import React from 'react'

import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { computeURLCollectiveOfferId } from 'core/OfferEducational/utils/computeURLCollectiveOfferId'
import { Audience } from 'core/shared'

import OfferItem from '../OfferItem/OfferItem'

type OffersTableBodyProps = {
  areAllOffersSelected: boolean
  offers: (CollectiveOfferResponseModel | ListOffersOfferResponseModel)[]
  selectOffer: (
    offerId: number,
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
    {offers.map((offer) => {
      const offerId = computeURLCollectiveOfferId(
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
