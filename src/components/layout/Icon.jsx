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
  className: null,
  name: null,
  src: null,
  svg: null
}

 Icon.propTypes = {
  className: PropTypes.string,
  name: PropTypes.string,
  src: PropTypes.string,
  svg: PropTypes.string
}

 export default Icon
