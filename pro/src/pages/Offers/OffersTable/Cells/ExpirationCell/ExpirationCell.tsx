import classNames from 'classnames'
import { differenceInCalendarDays } from 'date-fns'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
} from 'apiClient/v1'
import fullInfoIcon from 'icons/full-info.svg'
import fullWaitIcon from 'icons/full-wait.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { pluralize } from 'utils/pluralize'

import { getDate } from '../OfferNameCell/utils'

import styles from './ExpirationCell.module.scss'

export type ExpirationCellProps = {
  offer: CollectiveOfferResponseModel
  headers?: string
}

export function ExpirationCell({ offer, headers }: ExpirationCellProps) {
  const daysCountBeforeExpiration = offer.stocks[0].bookingLimitDatetime
    ? differenceInCalendarDays(
        new Date(offer.stocks[0].bookingLimitDatetime),
        new Date()
      )
    : 0

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
              : 'résevation'}{' '}
            par l’enseignant
          </div>
        </div>
        <div className={styles['banner-booking-date']}>
          date limite de réservation : {getDate(offer.stocks[0])}
        </div>
      </div>
    </td>
  )
}
