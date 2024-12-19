import cn from 'classnames'

import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { CollectiveStatusLabel } from 'components/CollectiveStatusLabel/CollectiveStatusLabel'
import styles from 'styles/components/Cells.module.scss'

import { ExpirationBanner } from '../ExpirationBanner/ExpirationBanner'

interface CollectiveOfferStatusCellProps {
  offer: CollectiveOfferResponseModel
  className?: string
  hasExpirationRow: boolean
  bookingLimitDate?: string | null
}

export const CollectiveOfferStatusCell = ({
  offer,
  className,
  hasExpirationRow,
  bookingLimitDate,
}: CollectiveOfferStatusCellProps) => {
  return (
    <td
      className={cn(
        styles['offers-table-cell'],
        styles['status-column'],
        className
      )}
    >
      <CollectiveStatusLabel offerDisplayedStatus={offer.displayedStatus} />
      {hasExpirationRow && bookingLimitDate && (
        <div className={styles['visually-hidden']}>
          <ExpirationBanner offer={offer} bookingLimitDate={bookingLimitDate} />
        </div>
      )}
    </td>
  )
}
