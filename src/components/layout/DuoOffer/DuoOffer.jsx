import PropTypes from 'prop-types'
import React from 'react'

const DuoOffer = ({ isDuoOffer, label }) =>
  isDuoOffer && (
    <div className="duo">
      <span className="duo-logo">
        {'duo'}
      </span>
      {label && <span className="duo-label">
        {label}
      </span>}
    </div>
  )

DuoOffer.defaultProps = {
  isDuoOffer: false,
  label: '',
}

DuoOffer.propTypes = {
  isDuoOffer: PropTypes.bool,
  label: PropTypes.string,
  offerId: PropTypes.string.isRequired,
}

export default DuoOffer
