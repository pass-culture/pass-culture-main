import cn from 'classnames'

import {
  CollectiveOfferResponseModel,
  CollectiveOfferStatus,
} from 'apiClient/v1'
import { CollectiveStatusLabel } from 'components/CollectiveStatusLabel/CollectiveStatusLabel'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import strokeDoubleCheckIcon from 'icons/stroke-double-check.svg'
import strokeHourglassIcon from 'icons/stroke-hourglass.svg'
import strokeThing from 'icons/stroke-thing.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from '../../OfferRow.module.scss'

import style from './CollectiveOfferStatusCell.module.scss'

export const getCollectiveStatusLabel = (
  offerStatus: CollectiveOfferStatus,
  lastBookingStatus?: string
) => {
  switch (offerStatus) {
    case CollectiveOfferStatus.PENDING:
      return (
        <CollectiveStatusLabel
          className={style['status-pending']}
          icon={
            <SvgIcon
              className={cn(style['status-label-icon'])}
              src={strokeClockIcon}
              alt=""
            />
          }
          label="en attente"
        />
      )

    case CollectiveOfferStatus.REJECTED:
      return (
        <CollectiveStatusLabel
          className={style['status-rejected']}
          icon={
            <SvgIcon
              alt=""
              src={strokeCloseIcon}
              className={style['status-label-icon']}
            />
          }
          label="refusée"
        />
      )
    case CollectiveOfferStatus.INACTIVE:
      return (
        <CollectiveStatusLabel
          className={style['status-inactive']}
          icon={
            <SvgIcon
              alt=""
              src={fullHideIcon}
              className={style['status-label-icon']}
            />
          }
          label="masquée"
        />
      )
    case CollectiveOfferStatus.ACTIVE:
      return (
        <CollectiveStatusLabel
          className={style['status-active']}
          icon={
            <SvgIcon
              src={strokeCheckIcon}
              alt=""
              className={style['status-label-icon']}
            />
          }
          label="publiée"
        />
      )
    case CollectiveOfferStatus.SOLD_OUT:
      return lastBookingStatus === 'PENDING' ? (
        <CollectiveStatusLabel
          className={style['status-pre-booked']}
          icon={
            <SvgIcon
              className={cn(
                style['status-label-icon'],
                style['status-pre-booked-icon']
              )}
              src={strokeHourglassIcon}
              alt=""
            />
          }
          label="préréservée"
        />
      ) : (
        <CollectiveStatusLabel
          className={style['status-booked']}
          icon={
            <SvgIcon
              src={strokeCheckIcon}
              alt=""
              className={style['status-label-icon']}
            />
          }
          label="réservée"
        />
      )
    case CollectiveOfferStatus.EXPIRED:
      return lastBookingStatus && lastBookingStatus !== 'CANCELLED' ? (
        <CollectiveStatusLabel
          className={style['status-ended']}
          icon={
            <SvgIcon
              alt=""
              src={strokeDoubleCheckIcon}
              className={style['status-label-icon']}
            />
          }
          label="terminée"
        />
      ) : (
        <CollectiveStatusLabel
          className={style['status-expired']}
          icon={
            <SvgIcon
              alt=""
              src={strokeCalendarIcon}
              className={style['status-label-icon']}
            />
          }
          label="expirée"
        />
      )
    case CollectiveOfferStatus.ARCHIVED:
      return (
        <CollectiveStatusLabel
          className={style['status-archived']}
          icon={
            <SvgIcon
              alt=""
              src={strokeThing}
              className={cn(
                style['status-label-icon'],
                style['status-archived-icon']
              )}
            />
          }
          label="archivée"
        />
      )
    default:
      throw Error('Le statut de l’offre n’est pas valide')
  }
}

interface CollectiveOfferStatusCellProps {
  offer: CollectiveOfferResponseModel
}

export const CollectiveOfferStatusCell = ({
  offer,
}: CollectiveOfferStatusCellProps) => (
  <td className={styles['status-column']}>
    {getCollectiveStatusLabel(offer.status, offer.booking?.booking_status)}
  </td>
)
