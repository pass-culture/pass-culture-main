import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { isSameOffer } from 'commons/utils/isSameOffer'

import { CollectiveOfferRow } from '../CollectiveOfferRow/CollectiveOfferRow'

import styles from './CollectiveOffersTableBody.module.scss'

type CollectiveOffersTableBodyProps = {
  offers: CollectiveOfferResponseModel[]
  selectOffer: (offer: CollectiveOfferResponseModel) => void
  selectedOffers: CollectiveOfferResponseModel[]
  urlSearchFilters: CollectiveSearchFiltersParams
}

export const CollectiveOffersTableBody = ({
  offers,
  selectOffer,
  selectedOffers,
  urlSearchFilters,
}: CollectiveOffersTableBodyProps) => {
  return (
    <tbody className={styles['collective-tbody']}>
      {offers.map((offer, index) => {
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
            isFirstRow={index === 0}
          />
        )
      })}
    </tbody>
  )
}
