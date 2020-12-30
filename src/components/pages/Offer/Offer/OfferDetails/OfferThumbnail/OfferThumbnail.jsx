import PropTypes from 'prop-types'
import React from 'react'

import Icon from 'components/layout/Icon'

const OfferThumbnail = ({ url }) => (
  <button
    className="of-placeholder of-image"
    title="Modifier l’image"
    type="button"
  >
    <Icon
      alt="Image de l’offre"
      src={url}
    />
  </button>
)

OfferThumbnail.propTypes = {
  url: PropTypes.string.isRequired,
}

export default OfferThumbnail
