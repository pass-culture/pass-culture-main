import PropTypes from 'prop-types'
import React from 'react'

import { SVGOffers } from '../svg/SVGOffers'

const Thumb = ({ url, alt }) => {
  return url ? (
    <img alt={alt} className="offer-thumb" loading="lazy" src={url} />
  ) : (
    <div className="default-thumb">
      <SVGOffers alt={alt} />
    </div>
  )
}

Thumb.defaultProps = {
  alt: '',
  url: '',
}

Thumb.propTypes = {
  alt: PropTypes.string,
  url: PropTypes.string,
}

export default Thumb
