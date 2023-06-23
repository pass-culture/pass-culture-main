import cn from 'classnames'
import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import { CollectiveStatusLabel } from 'components/CollectiveStatusLabel'
import { Offer } from 'core/Offers/types'
import { ReactComponent as StatusEndedIcon } from 'icons/ico-double-check.svg'
import { ReactComponent as StatusExpiredIcon } from 'icons/ico-status-expired.svg'
import { ReactComponent as StatusInactiveIcon } from 'icons/ico-status-inactive.svg'
import { ReactComponent as StatusPendingIcon } from 'icons/ico-status-pending.svg'
import { ReactComponent as StatusRejectedIcon } from 'icons/ico-status-rejected.svg'
import { ReactComponent as StatusValidatedIcon } from 'icons/ico-status-validated.svg'
import strokeHourglass from 'icons/stroke-hourglass.svg'
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
          icon={<StatusPendingIcon className={style['status-label-icon']} />}
          label="en attente"
        />
      )

    case OfferStatus.REJECTED:
      return (
        <CollectiveStatusLabel
          className={style['status-rejected']}
          icon={<StatusRejectedIcon className={style['status-label-icon']} />}
          label="refusée"
        />
      )
    case OfferStatus.INACTIVE:
      return (
        <CollectiveStatusLabel
          className={style['status-inactive']}
          icon={<StatusInactiveIcon className={style['status-label-icon']} />}
          label="désactivée"
        />
      )
    case OfferStatus.ACTIVE:
      return (
        <CollectiveStatusLabel
          className={style['status-active']}
          icon={<StatusValidatedIcon className={style['status-label-icon']} />}
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
              src={strokeHourglass}
              alt=""
            />
          }
          label="préréservée"
        />
      ) : (
        <CollectiveStatusLabel
          className={style['status-booked']}
          icon={<StatusValidatedIcon className={style['status-label-icon']} />}
          label="réservée"
        />
      )
    case OfferStatus.EXPIRED:
      return lastBookingStatus && lastBookingStatus != 'CANCELLED' ? (
        <CollectiveStatusLabel
          className={style['status-ended']}
          icon={<StatusEndedIcon className={style['status-label-icon']} />}
          label="terminée"
        />
      ) : (
        <CollectiveStatusLabel
          className={style['status-expired']}
          icon={<StatusExpiredIcon className={style['status-label-icon']} />}
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
