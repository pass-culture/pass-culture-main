import PropTypes from 'prop-types'
import React from 'react'

import { ICONS_URL } from '../../../utils/config'

const Icon = ({ alt, svg, className }) => (
  <img
    alt={alt}
    className={className}
    src={`${ICONS_URL}/${svg}.svg`}
  />
)

Icon.defaultProps = {
  alt: '',
  className: '',
}

Icon.propTypes = {
  alt: PropTypes.string,
  className: PropTypes.string,
  svg: PropTypes.string.isRequired,
}

export default Icon
