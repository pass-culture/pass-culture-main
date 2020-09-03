import PropTypes from 'prop-types'
import React from 'react'

import { SVGOffers } from '../svg/SVGOffers'

const Thumb = ({ url }) => {
  return url ? (
    <img
      alt=""
      className="offer-thumb"
      src={url}
    />
  ) : (
    <div className="default-thumb">
      <SVGOffers />
    </div>
  )
}

Thumb.defaultProps = {
  url: '',
}

Thumb.propTypes = {
  url: PropTypes.string,
}

export default Thumb
