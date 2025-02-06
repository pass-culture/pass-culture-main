import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { isSameOffer } from 'commons/utils/isSameOffer'

import { IndividualOfferRow } from '../IndividualOfferRow/IndividualOfferRow'

import styles from './IndividualOffersTableBody.module.scss'

type IndividualOffersTableBodyProps = {
  offers: ListOffersOfferResponseModel[]
  selectOffer: (offer: ListOffersOfferResponseModel) => void
  selectedOffers: ListOffersOfferResponseModel[]
}

export const IndividualOffersTableBody = ({
  offers,
  selectOffer,
  selectedOffers,
}: IndividualOffersTableBodyProps) => {
  return (
    <tbody role="rowgroup" className={styles['individual-tbody']}>
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
