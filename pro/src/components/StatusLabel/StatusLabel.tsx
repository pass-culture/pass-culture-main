import cn from 'classnames'
import React, { ReactElement } from 'react'

import { OfferStatus } from 'apiClient/v1'
import { ReactComponent as StatusDraftIcon } from 'icons/ico-status-draft.svg'
import { ReactComponent as StatusExpiredIcon } from 'icons/ico-status-expired.svg'
import { ReactComponent as StatusInactiveIcon } from 'icons/ico-status-inactive.svg'
import { ReactComponent as StatusPendingIcon } from 'icons/ico-status-pending.svg'
import { ReactComponent as StatusRejectedIcon } from 'icons/ico-status-rejected.svg'
import { ReactComponent as StatusSoldOutIcon } from 'icons/ico-status-sold-out.svg'
import { ReactComponent as StatusValidatedIcon } from 'icons/ico-status-validated.svg'

import style from './StatusLabel.module.scss'

const OFFER_STATUS_PROPERTIES: Record<
  string,
  {
    className: string
    Icon: ReactElement
    label: string
  }
> = {
  [OfferStatus.EXPIRED]: {
    className: style['status-expired'],
    Icon: <StatusExpiredIcon />,
    label: 'expirée',
  },
  [OfferStatus.SOLD_OUT]: {
    className: style['status-sold-out'],
    Icon: <StatusSoldOutIcon />,
    label: 'épuisée',
  },
  [OfferStatus.ACTIVE]: {
    className: style['status-active'],
    Icon: <StatusValidatedIcon />,
    label: 'publiée',
  },
  [OfferStatus.DRAFT]: {
    className: style['status-draft'],
    Icon: <StatusDraftIcon />,
    label: 'brouillon',
  },
  [OfferStatus.REJECTED]: {
    className: style['status-rejected'],
    Icon: <StatusRejectedIcon />,
    label: 'refusée',
  },
  [OfferStatus.PENDING]: {
    className: style['status-pending'],
    Icon: <StatusPendingIcon />,
    label: 'en attente',
  },
  [OfferStatus.INACTIVE]: {
    className: style['status-inactive'],
    Icon: <StatusInactiveIcon />,
    label: 'désactivée',
  },
}

type StatusLabelProps = {
  status: OfferStatus
}
const StatusLabel = ({ status }: StatusLabelProps) => {
  return (
    <span
      className={cn(
        style['status-label'],
        OFFER_STATUS_PROPERTIES[status]?.className
      )}
    >
      <>
        {OFFER_STATUS_PROPERTIES[status]?.Icon}
        {OFFER_STATUS_PROPERTIES[status]?.label}
      </>
    </span>
  )
}
export default StatusLabel
