import {
  OFFER_STATUS_ACTIVE,
  OFFER_STATUS_EXPIRED,
  OFFER_STATUS_INACTIVE,
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
  OFFER_STATUS_SOLD_OUT,
} from 'core/Offers/constants'

import Icon from 'components/layout/Icon'
import PropTypes from 'prop-types'
import React from 'react'

export const OFFER_STATUS_PROPERTIES = {
  [OFFER_STATUS_EXPIRED]: {
    className: 'status-expired',
    icon: 'ico-status-expired',
    label: 'expirée',
  },
  [OFFER_STATUS_SOLD_OUT]: {
    className: 'status-sold-out',
    icon: 'ico-status-sold-out',
    label: 'épuisée',
  },
  [OFFER_STATUS_ACTIVE]: {
    className: 'status-active',
    icon: 'ico-status-validated',
    label: 'active',
  },
  [OFFER_STATUS_REJECTED]: {
    className: 'status-rejected',
    icon: 'ico-status-rejected',
    label: 'refusée',
  },
  [OFFER_STATUS_PENDING]: {
    className: 'status-pending',
    icon: 'ico-status-pending',
    label: 'en attente',
  },
  [OFFER_STATUS_INACTIVE]: {
    className: 'status-inactive',
    icon: 'ico-status-inactive',
    label: 'désactivée',
  },
}

const StatusLabel = ({ status }) => {
  return (
    <span
      className={`op-offer-status ${OFFER_STATUS_PROPERTIES[status]?.className}`}
    >
      <Icon svg={OFFER_STATUS_PROPERTIES[status]?.icon} />
      {OFFER_STATUS_PROPERTIES[status]?.label}
    </span>
  )
}

StatusLabel.propTypes = {
  status: PropTypes.string.isRequired,
}

export default StatusLabel
