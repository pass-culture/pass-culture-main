import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { SearchFiltersParams } from 'core/Offers/types'
import { isSameOffer } from 'pages/Offers/utils/isSameOffer'

import { CollectiveOfferRow } from './CollectiveOfferRow/CollectiveOfferRow'

type CollectiveOffersTableBodyProps = {
  offers: CollectiveOfferResponseModel[]
  selectOffer: (offer: CollectiveOfferResponseModel) => void
  selectedOffers: CollectiveOfferResponseModel[]
  urlSearchFilters: SearchFiltersParams
}

export const CollectiveOffersTableBody = ({
  offers,
  selectOffer,
  selectedOffers,
  urlSearchFilters,
}: CollectiveOffersTableBodyProps) => {
  return (
    <tbody className="offers-list">
      {offers.map((offer) => {
        const isSelected = selectedOffers.some((selectedOffer) =>
          isSameOffer(selectedOffer, offer)
        )

        return (
          <CollectiveOfferRow
            isSelected={isSelected}
            key={`${offer.isShowcase ? 'T-' : ''}${offer.id}`}
            offer={offer}
            selectOffer={selectOffer}
            urlSearchFilters={urlSearchFilters}
          />
        )
      })}
    </tbody>
  )
}
