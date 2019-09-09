import PropTypes from 'prop-types'
import React from 'react'

import { ROOT_PATH } from '../../utils/config'

export const getImageUrl = (svg, png) => {
  let iconUrl
  svg ? (iconUrl = `${ROOT_PATH}/icons/${svg}.svg`) : (iconUrl = `${ROOT_PATH}/icons/${png}.png`)
  return iconUrl
}

const Icon = ({ png, svg, ...imgProps }) => {
  let altMessage
  const iconUrl = getImageUrl(svg, png)
  svg ? (altMessage = svg) : (altMessage = png)
  return (<img
    alt={altMessage}
    src={iconUrl}
    {...imgProps}
          />)
}

Icon.defaultProps = {
  png: null,
}

Icon.propTypes = {
  png: PropTypes.string,
  svg: PropTypes.string.isRequired,
}

export default Icon
