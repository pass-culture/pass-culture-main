import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'

const OfferCover = ({ url }) => (
  <div className="of-placeholder">
    <Icon
      alt="Couverture de l’offre"
      src={url}
    />
  </div>
)

OfferCover.propTypes = {
  url: PropTypes.string.isRequired,
}

export default OfferCover
