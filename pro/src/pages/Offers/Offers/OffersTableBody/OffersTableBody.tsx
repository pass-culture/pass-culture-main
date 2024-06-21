import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { SearchFiltersParams } from 'core/Offers/types'
import { Audience } from 'core/shared/types'

import { OfferItem } from '../OfferItem/OfferItem'
import { isSameOffer } from '../utils'

type OffersTableBodyProps = {
  offers: CollectiveOfferResponseModel[] | ListOffersOfferResponseModel[]
  selectOffer: (
    offer: CollectiveOfferResponseModel | ListOffersOfferResponseModel
  ) => void
  selectedOffers:
    | CollectiveOfferResponseModel[]
    | ListOffersOfferResponseModel[]
  audience: Audience
  urlSearchFilters: SearchFiltersParams
}

export const OffersTableBody = ({
  offers,
  selectOffer,
  selectedOffers,
  audience,
  urlSearchFilters,
}: OffersTableBodyProps) => {
  return (
    <tbody className="offers-list">
      {offers.map((offer) => {
        const isSelected = selectedOffers.some((selectedOffer) =>
          isSameOffer(selectedOffer, offer)
        )

        return (
          <OfferItem
            isSelected={isSelected}
            key={`${offer.isShowcase ? 'T-' : ''}${offer.id}`}
            offer={offer}
            selectOffer={selectOffer}
            audience={audience}
            urlSearchFilters={urlSearchFilters}
          />
        )
      })}
    </tbody>
  )
}
