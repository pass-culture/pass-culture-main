import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { isSameOffer } from 'pages/Offers/utils/isSameOffer'

import { IndividualOfferRow } from '../OfferRow/IndividualOfferRow'

type IndividualOffersTableBodyProps = {
  offers: ListOffersOfferResponseModel[]
  selectOffer: (
    offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  ) => void
  selectedOffers: ListOffersOfferResponseModel[]
}

export const IndividualOffersTableBody = ({
  offers,
  selectOffer,
  selectedOffers,
}: IndividualOffersTableBodyProps) => {
  return (
    <tbody className="offers-list">
      {offers.map((offer) => {
        const isSelected = selectedOffers.some((selectedOffer) =>
          isSameOffer(selectedOffer, offer)
        )

        return (
          <IndividualOfferRow
            isSelected={isSelected}
            key={offer.id}
            offer={offer}
            selectOffer={selectOffer}
          />
        )
      })}
    </tbody>
  )
}
