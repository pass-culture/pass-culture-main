import PropTypes from 'prop-types'
import React from 'react'

import { ROOT_PATH } from '../../utils/config'

const Icon = ({ png, svg, alt, ...imgProps }) => {
  const iconUrl = svg ? `${ROOT_PATH}/icons/${svg}.svg` : `${ROOT_PATH}/icons/${png}.png`
  return (
    <img
      alt={alt}
      src={iconUrl}
      {...imgProps}
    />
  )
}

Icon.defaultProps = {
  alt: '',
  png: null,
  svg: null,
}

Icon.propTypes = {
  alt: PropTypes.string,
  png: PropTypes.string,
  svg: PropTypes.string,
}

export default Icon
