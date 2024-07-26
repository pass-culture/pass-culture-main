import classNames from 'classnames'
import { differenceInCalendarDays, format } from 'date-fns'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
} from 'apiClient/v1'
import fullInfoIcon from 'icons/full-info.svg'
import fullWaitIcon from 'icons/full-wait.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { FORMAT_DD_MM_YYYY, toDateStrippedOfTimezone } from 'utils/date'
import { pluralize } from 'utils/pluralize'

import styles from './ExpirationCell.module.scss'

type ExpirationCellProps = {
  offer: CollectiveOfferResponseModel
  headers?: string
  bookingLimitDate: string
}

export function ExpirationCell({
  offer,
  headers,
  bookingLimitDate,
}: ExpirationCellProps) {
  const daysCountBeforeExpiration = differenceInCalendarDays(
    new Date(bookingLimitDate),
    new Date()
  )

  return (
    <td colSpan={8} headers={headers} className={styles['expiration-cell']}>
      <div
        className={classNames(styles['banner'], {
          [styles['banner-expires-soon']]: daysCountBeforeExpiration <= 7,
        })}
      >
        <div className={styles['banner-expiration']}>
          {daysCountBeforeExpiration <= 7 && (
            <div className={styles['banner-expiration-days-badge']}>
              <SvgIcon alt="" src={fullInfoIcon} width="16" />
              <div>
                expire{' '}
                {daysCountBeforeExpiration > 0
                  ? `dans ${pluralize(daysCountBeforeExpiration, 'jour')}`
                  : 'aujourd’hui'}
              </div>
            </div>
          )}
          <div className={styles['banner-expiration-waiting']}>
            <SvgIcon alt="" src={fullWaitIcon} width="16" /> En attente de{' '}
            {offer.status === CollectiveOfferStatus.ACTIVE
              ? 'préréservation'
              : 'réservation'}{' '}
            par l’enseignant
          </div>
        </div>
        <div className={styles['banner-booking-date']}>
          date limite de réservation :{' '}
          {format(
            toDateStrippedOfTimezone(bookingLimitDate.toString()),
            FORMAT_DD_MM_YYYY
          )}
        </div>
      </div>
    </td>
  )
}
