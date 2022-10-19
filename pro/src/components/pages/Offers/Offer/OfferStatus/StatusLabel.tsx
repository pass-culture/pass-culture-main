import React from 'react'

import { OfferStatus } from 'apiClient/v1'
import Icon from 'components/layout/Icon'

export const OFFER_STATUS_PROPERTIES: Record<
  string,
  { className: string; icon: string; label: string }
> = {
  [OfferStatus.EXPIRED]: {
    className: 'status-expired',
    icon: 'ico-status-expired',
    label: 'expirée',
  },
  [OfferStatus.SOLD_OUT]: {
    className: 'status-sold-out',
    icon: 'ico-status-sold-out',
    label: 'épuisée',
  },
  [OfferStatus.ACTIVE]: {
    className: 'status-active',
    icon: 'ico-status-validated',
    label: 'publiée',
  },
  [OfferStatus.DRAFT]: {
    className: 'status-draft',
    icon: 'ico-status-draft',
    label: 'brouillon',
  },
  [OfferStatus.REJECTED]: {
    className: 'status-rejected',
    icon: 'ico-status-rejected',
    label: 'refusée',
  },
  [OfferStatus.PENDING]: {
    className: 'status-pending',
    icon: 'ico-status-pending',
    label: 'en attente',
  },
  [OfferStatus.INACTIVE]: {
    className: 'status-inactive',
    icon: 'ico-status-inactive',
    label: 'désactivée',
  },
}

type StatusLabelProps = {
  status: string
}
const StatusLabel = ({ status }: StatusLabelProps) => {
  return (
    <span
      className={`op-offer-status ${OFFER_STATUS_PROPERTIES[status]?.className}`}
    >
      <Icon svg={OFFER_STATUS_PROPERTIES[status]?.icon} />
      {OFFER_STATUS_PROPERTIES[status]?.label}
    </span>
  )
}
export default StatusLabel
