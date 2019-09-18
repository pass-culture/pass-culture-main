import PropTypes from 'prop-types'
import React from 'react'

import { ROOT_PATH } from '../../utils/config'

const Icon = ({ png, svg, ...imgProps }) => {
  const altMessage = svg ? svg : png
  const iconUrl = svg ? `${ROOT_PATH}/icons/${svg}.svg` : `${ROOT_PATH}/icons/${png}.png`
  return (<img
    alt={altMessage}
    src={iconUrl}
    {...imgProps}
          />)
}

Icon.defaultProps = {
  png: null,
  svg: null,
}

Icon.propTypes = {
  png: PropTypes.string,
  svg: PropTypes.string,
}

export default Icon
