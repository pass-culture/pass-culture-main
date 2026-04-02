import classNames from 'classnames'
import { differenceInCalendarDays, format } from 'date-fns'

import {
  CollectiveOfferDisplayedStatus,
  type CollectiveOfferResponseModel,
} from '@/apiClient/v1'
import { getExpirationText } from '@/commons/core/OfferEducational/utils/getExpirationText'
import {
  FORMAT_DD_MM_YYYY,
  toDateStrippedOfTimezone,
} from '@/commons/utils/date'
import fullInfoIcon from '@/icons/full-info.svg'
import fullWaitIcon from '@/icons/full-wait.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ExpirationCell.module.scss'

type ExpirationCellProps = {
  offer: CollectiveOfferResponseModel
}

function isCollectiveOfferPublishedOrPreBooked(
  offer: CollectiveOfferResponseModel
) {
  return (
    offer.displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED ||
    offer.displayedStatus === CollectiveOfferDisplayedStatus.PREBOOKED
  )
}

export function ExpirationCell({ offer }: ExpirationCellProps) {
  const bookingLimitDate = offer.stock?.bookingLimitDatetime

  const daysCountBeforeExpiration = differenceInCalendarDays(
    new Date(bookingLimitDate ?? new Date()),
    new Date()
  )
  const hasExpirationRow =
    isCollectiveOfferPublishedOrPreBooked(offer) && !!bookingLimitDate

  if (!hasExpirationRow) {
    return null
  }

  const expirationText = getExpirationText(daysCountBeforeExpiration)
  const isExpiringSoon = !!expirationText

  return (
    <div
      className={classNames(styles['banner'], {
        [styles['banner-expires-soon']]: isExpiringSoon,
      })}
    >
      <div className={styles['banner-expiration']}>
        {isExpiringSoon && (
          <div className={styles['banner-expiration-days-badge']}>
            <SvgIcon alt="" src={fullInfoIcon} width="16" />
            <div>{expirationText}</div>
          </div>
        )}
        <div className={styles['banner-expiration-waiting']}>
          <SvgIcon alt="" src={fullWaitIcon} width="16" /> En attente de{' '}
          {offer.displayedStatus === CollectiveOfferDisplayedStatus.PUBLISHED
            ? 'préréservation par l’enseignant'
            : 'réservation par le chef d’établissement'}
        </div>
      </div>
      <div>
        date limite de réservation :{' '}
        {bookingLimitDate
          ? format(
              toDateStrippedOfTimezone(bookingLimitDate.toString()),
              FORMAT_DD_MM_YYYY
            )
          : '-'}
      </div>
    </div>
  )
}
