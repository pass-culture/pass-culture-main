import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { SearchFiltersParams } from 'core/Offers/types'
import { Audience } from 'core/shared/types'

import { OfferItem } from '../OfferItem/OfferItem'

type OffersTableBodyProps = {
  offers: CollectiveOfferResponseModel[] | ListOffersOfferResponseModel[]
  selectOffer: (offerId: number, isSelected: boolean) => void
  selectedOfferIds: number[]
  audience: Audience
  urlSearchFilters: SearchFiltersParams
}

export const OffersTableBody = ({
  offers,
  selectOffer,
  selectedOfferIds,
  audience,
  urlSearchFilters,
}: OffersTableBodyProps) => {
  return (
    <tbody className="offers-list">
      {offers.map((offer) => {
        return (
          <OfferItem
            isSelected={selectedOfferIds.includes(offer.id)}
            key={offer.id}
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
