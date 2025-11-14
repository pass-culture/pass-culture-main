import type { CollectiveOfferResponseModel } from '@/apiClient/v1'
import { pluralizeFr } from '@/commons/utils/pluralize'

import styles from './PriceAndParticipantsCell.module.scss'

interface PriceAndParticipantsCellProps {
  offer: CollectiveOfferResponseModel
}

export const PriceAndParticipantsCell = ({
  offer,
}: PriceAndParticipantsCellProps) => {
  const { price, numberOfTickets } = offer.stock || {}

  return (
    <div className={styles['price-and-participants-column']}>
      {price && numberOfTickets ? (
        <div className={styles['price-and-participants-container']}>
          <span>{price}€</span>
          <span>{`${numberOfTickets} ${pluralizeFr(numberOfTickets, 'participant', 'participants')}`}</span>
        </div>
      ) : (
        '-'
      )}
    </div>
  )
}
