import cn from 'classnames'

import {
  CollectiveOfferDisplayedStatus,
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

import styles from '../Cells.module.scss'

import style from './CollectiveOfferStatusCell.module.scss'

export const getCollectiveStatusLabel = (
  offerStatus: CollectiveOfferStatus,
  offerDisplayedStatus: CollectiveOfferDisplayedStatus
) => {
  switch (offerDisplayedStatus) {
    case CollectiveOfferDisplayedStatus.PENDING:
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

    case CollectiveOfferDisplayedStatus.REJECTED:
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
    case CollectiveOfferDisplayedStatus.INACTIVE:
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
    case CollectiveOfferDisplayedStatus.ACTIVE:
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
    case CollectiveOfferDisplayedStatus.PREBOOKED:
      return (
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
      )
    case CollectiveOfferDisplayedStatus.BOOKED:
      return (
        <CollectiveStatusLabel
          className={style['status-booked']}
          icon={
            <SvgIcon
              src={strokeClockIcon}
              alt=""
              className={style['status-label-icon']}
            />
          }
          label="réservée"
        />
      )
    case CollectiveOfferDisplayedStatus.EXPIRED:
      return (
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
    case CollectiveOfferDisplayedStatus.REIMBURSED:
    case CollectiveOfferDisplayedStatus.ENDED:
      return (
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
      )
    case CollectiveOfferDisplayedStatus.CANCELLED:
      return offerStatus === CollectiveOfferStatus.ACTIVE ? (
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
      ) : (
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
    case CollectiveOfferDisplayedStatus.ARCHIVED:
      return (
        <CollectiveStatusLabel
          className={style['status-archived']}
          icon={
            <SvgIcon
              alt=""
              src={strokeThing}
              className={style['status-label-icon']}
            />
          }
          label="archivée"
        />
      )
    case CollectiveOfferDisplayedStatus.DRAFT:
      return (
        <CollectiveStatusLabel
          className={style['status-draft']}
          icon={
            <SvgIcon
              alt=""
              src={strokeThing}
              className={cn(
                style['status-label-icon'],
                style['status-draft-icon']
              )}
            />
          }
          label="brouillon"
        />
      )
  }
}

interface CollectiveOfferStatusCellProps {
  offer: CollectiveOfferResponseModel
  headers?: string
}

export const CollectiveOfferStatusCell = ({
  offer,
  headers,
}: CollectiveOfferStatusCellProps) => (
  <td
    className={cn(styles['offers-table-cell'], styles['status-column'])}
    headers={headers}
  >
    {getCollectiveStatusLabel(offer.status, offer.displayedStatus)}
  </td>
)
