import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import fullHideIcon from 'icons/full-hide.svg'
import strokeCalendarIcon from 'icons/stroke-calendar.svg'
import strokeCheckIcon from 'icons/stroke-check.svg'
import strokeClockIcon from 'icons/stroke-clock.svg'
import strokeCloseIcon from 'icons/stroke-close.svg'
import strokeDraftIcon from 'icons/stroke-draft.svg'
import strokeWarningIcon from 'icons/stroke-warning.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'
import { Tag, TagVariant } from 'ui-kit/Tag/Tag'

const OFFER_STATUS_PROPERTIES: Record<
  OfferStatus,
  {
    variant: TagVariant
    icon: string
    label: string
  }
> = {
  [OfferStatus.EXPIRED]: {
    variant: TagVariant.DARK_GREY,
    icon: strokeCalendarIcon,
    label: 'expirée',
  },
  [OfferStatus.SOLD_OUT]: {
    variant: TagVariant.RED,
    icon: strokeWarningIcon,
    label: 'épuisée',
  },
  [OfferStatus.ACTIVE]: {
    variant: TagVariant.GREEN,
    icon: strokeCheckIcon,
    label: 'publiée',
  },
  [OfferStatus.DRAFT]: {
    variant: TagVariant.PURPLE,
    icon: strokeDraftIcon,
    label: 'brouillon',
  },
  [OfferStatus.REJECTED]: {
    variant: TagVariant.BLACK,
    icon: strokeCloseIcon,
    label: 'refusée',
  },
  [OfferStatus.PENDING]: {
    variant: TagVariant.DARK_GREY,
    icon: strokeClockIcon,
    label: 'en attente',
  },
  [OfferStatus.INACTIVE]: {
    variant: TagVariant.DARK_GREY,
    icon: fullHideIcon,
    label: 'désactivée',
  },
}

type StatusLabelProps = {
  status: OfferStatus
}

export const StatusLabel = ({ status }: StatusLabelProps) => {
  return (
    <Tag variant={OFFER_STATUS_PROPERTIES[status].variant}>
      <SvgIcon alt="" src={OFFER_STATUS_PROPERTIES[status].icon} />
      {OFFER_STATUS_PROPERTIES[status].label}
    </Tag>
  )
}
