import React from 'react'
import PropTypes from 'prop-types'

import { getDisplayPrice } from '../../../helpers'

const Price = ({ free, value, className, ...rest }) => {
  const price = getDisplayPrice(value, free)

  return (
    <span
      {...rest}
      className={className}
    >
      {price}
    </span>
  )
}

Price.defaultProps = {
  className: '',
  free: null,
  value: null,
}

Price.propTypes = {
  className: PropTypes.string,
  free: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.array, PropTypes.number]),
}

export default Price
