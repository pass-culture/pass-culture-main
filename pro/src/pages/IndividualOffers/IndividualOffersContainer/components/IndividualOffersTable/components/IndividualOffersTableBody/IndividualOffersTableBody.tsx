import { ListOffersOfferResponseModel } from 'apiClient/v1'
import { isSameOffer } from 'commons/utils/isSameOffer'

import { IndividualOfferRow } from '../IndividualOfferRow/IndividualOfferRow'

import styles from './IndividualOffersTableBody.module.scss'

type IndividualOffersTableBodyProps = {
  offers: ListOffersOfferResponseModel[]
  selectOffer: (offer: ListOffersOfferResponseModel) => void
  selectedOffers: ListOffersOfferResponseModel[]
  isRestrictedAsAdmin: boolean
}

export const IndividualOffersTableBody = ({
  offers,
  selectOffer,
  selectedOffers,
  isRestrictedAsAdmin,
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
            isRestrictedAsAdmin={isRestrictedAsAdmin}
          />
        )
      })}
    </tbody>
  )
}
