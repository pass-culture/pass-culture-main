import PropTypes from 'prop-types'
import React from 'react'

import { ROOT_PATH } from '../../utils/config'

const Icon = ({ svg, ...imgProps }) => (
  <img
    alt={svg}
    src={`${ROOT_PATH}/icons/${svg}.svg`}
    {...imgProps}
  />
)

Icon.propTypes = {
  svg: PropTypes.string.isRequired,
}

export default Icon
