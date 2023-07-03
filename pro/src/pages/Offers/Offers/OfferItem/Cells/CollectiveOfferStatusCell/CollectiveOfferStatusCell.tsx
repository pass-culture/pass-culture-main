import cn from 'classnames'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { CollectiveStatusLabel } from 'components/CollectiveStatusLabel'
import { Offer } from 'core/Offers/types'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import { ReactComponent as StrokeCheckIcon } from 'icons/stroke-check.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import strokeDoubleCheckIcon from 'icons/stroke-double-check.svg'
import strokeHourglassIcon from 'icons/stroke-hourglass.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from '../../OfferItem.module.scss'

import style from './CollectiveOfferStatusCell.module.scss'

export const getCollectiveStatusLabel = (
  offerStatus: OfferStatus,
  lastBookingStatus?: string
) => {
  switch (offerStatus) {
    case OfferStatus.PENDING:
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

    case OfferStatus.REJECTED:
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
    case OfferStatus.INACTIVE:
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
          label="désactivée"
        />
      )
    case OfferStatus.ACTIVE:
      return (
        <CollectiveStatusLabel
          className={style['status-active']}
          icon={<StrokeCheckIcon className={style['status-label-icon']} />}
          label="publiée"
        />
      )
    case OfferStatus.SOLD_OUT:
      return lastBookingStatus == 'PENDING' ? (
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
          icon={<StrokeCheckIcon className={style['status-label-icon']} />}
          label="réservée"
        />
      )
    case OfferStatus.EXPIRED:
      return lastBookingStatus && lastBookingStatus != 'CANCELLED' ? (
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
    default:
      throw Error("Le statut de l'offre n'est pas valide")
  }
}

const CollectiveOfferStatusCell = ({ offer }: { offer: Offer }) => (
  <td className={styles['status-column']}>
    {getCollectiveStatusLabel(
      offer.status,
      offer.educationalBooking?.booking_status
    )}
  </td>
)

export default CollectiveOfferStatusCell
