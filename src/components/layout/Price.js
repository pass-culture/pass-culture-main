import React from 'react'
import PropTypes from 'prop-types'

import { getDisplayPrice } from '../../helpers'

const Price = ({ format, free, value, className, ...rest }) => {
  const price = getDisplayPrice(value, free, format)
  const classes = `price ${className}`
  return (
    <span
      {...rest}
      className={classes}
    >
      {price}
    </span>
  )
}

Price.defaultProps = {
  className: '',
  format: null,
  free: null,
  value: null,
}

Price.propTypes = {
  className: PropTypes.string,
  format: PropTypes.func,
  free: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.array, PropTypes.number]),
}

export default Price
