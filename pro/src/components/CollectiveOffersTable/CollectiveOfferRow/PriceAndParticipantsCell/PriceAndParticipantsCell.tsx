import cn from 'classnames'

import type { CollectiveOfferResponseModel } from '@/apiClient/v1'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { getCellsDefinition } from '@/components/CollectiveOffersTable/utils/cellDefinitions'

import styles from '../Cells.module.scss'

interface PriceAndParticipantsCellProps {
  offer: CollectiveOfferResponseModel
  rowId: string
  className?: string
}

export const PriceAndParticipantsCell = ({
  rowId,
  offer,
  className,
}: PriceAndParticipantsCellProps) => {
  const { price, numberOfTickets } = offer.stock || {}

  return (
    <td
      className={cn(
        styles['offers-table-cell'],
        styles['price-and-participants-column'],
        className
      )}
      headers={`${rowId} ${getCellsDefinition().PRICE_AND_PARTICIPANTS.id}`}
    >
      {price && numberOfTickets ? (
        <div className={styles['price-and-participants-container']}>
          <span>{price}€</span>
          <span>{`${numberOfTickets} ${pluralizeFr(numberOfTickets, 'participant', 'participants')}`}</span>
        </div>
      ) : (
        '-'
      )}
    </td>
  )
}
