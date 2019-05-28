import PropTypes from 'prop-types'
import React from 'react'

import { ICONS_URL } from '../../utils/config'

const Icon = ({ alt, name, src, svg, ...imgProps }) => (
  <img
    {...imgProps}
    alt={alt || svg}
    src={src || `${ICONS_URL}/${svg}.svg`}
  />
)

Icon.defaultProps = {
  name: null,
  src: null,
  svg: null
}

Icon.propTypes = {
  name: PropTypes.string,
  src: PropTypes.string,
  svg: PropTypes.string
}

export default Icon
