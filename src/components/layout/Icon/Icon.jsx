import PropTypes from 'prop-types'
import React from 'react'

import { ICONS_URL } from '../../../utils/config'

const Icon = ({ alt, svg, png, className }) => (
  <img
    alt={alt}
    className={className}
    src={`${ICONS_URL}/${svg ? `${svg}.svg` : `${png}.png`}`}
  />
)

Icon.defaultProps = {
  alt: '',
  className: null,
  png: null,
  svg: null,
}

Icon.propTypes = {
  alt: PropTypes.string,
  className: PropTypes.string,
  png: PropTypes.string,
  svg: PropTypes.string,
}

export default Icon
