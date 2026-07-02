import type { CollectiveOfferResponseModel } from '@/apiClient/v1'
import { pluralizeFr } from '@/commons/utils/pluralize'

import styles from './PriceAndParticipantsCell.module.scss'

interface PriceAndParticipantsCellProps {
  offer: CollectiveOfferResponseModel
}

export const PriceAndParticipantsCell = ({
  offer,
}: PriceAndParticipantsCellProps) => {
  const { price, numberOfTickets, numberOfTeachers } = offer.stock || {}
  const numberOfParticipants = (numberOfTickets || 0) + (numberOfTeachers || 0)

  return (
    <div className={styles['price-and-participants-column']}>
      {price && numberOfParticipants ? (
        <div className={styles['price-and-participants-container']}>
          <span>{price}€</span>
          <span>{`${numberOfParticipants} ${pluralizeFr(numberOfParticipants, 'participant', 'participants')}`}</span>
        </div>
      ) : (
        '-'
      )}
    </div>
  )
}
