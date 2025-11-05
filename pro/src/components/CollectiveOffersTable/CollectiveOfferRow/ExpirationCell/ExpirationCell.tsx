import classNames from 'classnames'
import { differenceInCalendarDays, format } from 'date-fns'

import {
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
} from '@/apiClient/v1'
import {
  FORMAT_DD_MM_YYYY,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { getCellsDefinition } from '@/components/CollectiveOffersTable/utils/cellDefinitions'
import fullInfoIcon from '@/icons/full-info.svg'
import fullWaitIcon from '@/icons/full-wait.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ExpirationCell.module.scss'

type ExpirationCellProps = {
  offer: CollectiveOfferResponseModel
  rowId: string
  className?: string
}

export function ExpirationCell({
  offer,
  rowId,
  className,
}: ExpirationCellProps) {
  const bookingLimitDate = String(offer.stock?.bookingLimitDatetime)

  const daysCountBeforeExpiration = differenceInCalendarDays(
    new Date(bookingLimitDate),
    new Date()
  )

  return (
    <td
      // biome-ignore lint/a11y: accepted for assistive tech
      role="cell"
      colSpan={8}
      headers={`${rowId} ${getCellsDefinition().INFO_ON_EXPIRATION.id}`}
      className={classNames(styles['expiration-cell'], className)}
    >
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
                  ? `dans ${daysCountBeforeExpiration} ${pluralizeFr(daysCountBeforeExpiration, 'jour', 'jours')}`
                  : 'aujourd’hui'}
              </div>
            </div>
          )}
          <div className={styles['banner-expiration-waiting']}>
            <SvgIcon alt="" src={fullWaitIcon} width="16" /> En attente de{' '}
            {offer.displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED
              ? 'préréservation par l’enseignant'
              : 'réservation par le chef d’établissement'}
          </div>
        </div>
        <div className={styles['banner-booking-date']}>
          date limite de réservation :{' '}
          {format(
            toDateStrippedOfTimezone(bookingLimitDate),
            FORMAT_DD_MM_YYYY
          )}
        </div>
      </div>
    </td>
  )
}
