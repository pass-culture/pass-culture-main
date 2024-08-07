import {
  CollectiveOfferResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'
import { isSameOffer } from 'pages/Offers/utils/isSameOffer'

import { IndividualOfferRow } from '../IndividualOfferRow/IndividualOfferRow'

import styles from './IndividualOffersTableBody.module.scss'

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
    <tbody className={styles['individual-tbody']}>
      {offers.map((offer, index) => {
        const isSelected = selectedOffers.some((selectedOffer) =>
          isSameOffer(selectedOffer, offer)
        )

        return (
          <IndividualOfferRow
            isSelected={isSelected}
            key={offer.id}
            offer={offer}
            selectOffer={selectOffer}
            isFirstRow={index === 0}
          />
        )
      })}
    </tbody>
  )
}
