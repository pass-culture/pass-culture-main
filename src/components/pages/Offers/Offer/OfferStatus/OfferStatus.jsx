import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'
import { OFFER_STATUS } from 'components/pages/Offers/Offers/domain/offerStatus'

export const OFFER_STATUS_PROPERTIES = {
  [OFFER_STATUS.EXPIRED]: {
    className: 'status-expired',
    icon: 'ico-status-expired',
    label: 'expirée',
  },
  [OFFER_STATUS.SOLD_OUT]: {
    className: 'status-sold-out',
    icon: 'ico-status-sold-out',
    label: 'épuisée',
  },
  [OFFER_STATUS.ACTIVE]: {
    className: 'status-active',
    icon: 'ico-status-validated',
    label: 'active',
  },
  [OFFER_STATUS.REJECTED]: {
    className: 'status-rejected',
    icon: 'ico-status-rejected',
    label: 'refusée',
  },
  [OFFER_STATUS.AWAITING]: {
    className: 'status-awaiting',
    icon: 'ico-status-awaiting',
    label: 'en attente',
  },
  [OFFER_STATUS.VALIDATED]: {
    className: 'status-validated',
    icon: 'ico-status-validated',
    label: 'validée',
  },
}

const OfferStatus = ({ status }) => {
  return (
    <span className={`op-offer-status ${OFFER_STATUS_PROPERTIES[status].className}`}>
      <Icon svg={OFFER_STATUS_PROPERTIES[status].icon} />
      {OFFER_STATUS_PROPERTIES[status].label}
    </span>
  )
}

OfferStatus.propTypes = {
  status: PropTypes.string.isRequired,
}

export default OfferStatus
