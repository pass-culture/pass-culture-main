import cn from 'classnames'
import React, { ReactElement } from 'react'

import { OfferStatus } from 'apiClient/v1'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import strokeDraftIcon from 'icons/stroke-draft.svg'
import strokeWarningIcon from 'icons/stroke-warning.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

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
    Icon: <SvgIcon alt="" src={strokeCalendarIcon} />,
    label: 'expirée',
  },
  [OfferStatus.SOLD_OUT]: {
    className: style['status-sold-out'],
    Icon: <SvgIcon alt="" src={strokeWarningIcon} />,
    label: 'épuisée',
  },
  [OfferStatus.ACTIVE]: {
    className: style['status-active'],
    Icon: <SvgIcon alt="" src={strokeCheckIcon} />,
    label: 'publiée',
  },
  [OfferStatus.DRAFT]: {
    className: style['status-draft'],
    Icon: <SvgIcon alt="" src={strokeDraftIcon} />,
    label: 'brouillon',
  },
  [OfferStatus.REJECTED]: {
    className: style['status-rejected'],
    Icon: <SvgIcon alt="" src={strokeCloseIcon} />,
    label: 'refusée',
  },
  [OfferStatus.PENDING]: {
    className: style['status-pending'],
    Icon: <SvgIcon alt="" src={strokeClockIcon} />,
    label: 'en attente',
  },
  [OfferStatus.INACTIVE]: {
    className: style['status-inactive'],
    Icon: <SvgIcon alt="" src={fullHideIcon} />,
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
