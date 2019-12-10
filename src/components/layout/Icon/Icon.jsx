import PropTypes from 'prop-types'
import React from 'react'

import { ICONS_URL } from '../../../utils/config'

const Icon = ({ alt, src, svg, png, ...imgProps }) => (
  <img
    {...imgProps}
    alt={alt || svg}
    src={src || `${ICONS_URL}/${svg ? `${svg}.svg` : `${png}.png`}`}
  />
)

Icon.defaultProps = {
  alt: null,
  className: null,
  png: null,
  src: null,
  svg: null,
}

Icon.propTypes = {
  alt: PropTypes.string,
  className: PropTypes.string,
  png: PropTypes.string,
  src: PropTypes.string,
  svg: PropTypes.string,
}

export default Icon
