import React from 'react'
import PropTypes from 'prop-types'

import { getPrice } from '../helpers'

const Price = ({ value, free, className }) => {
  const price = getPrice(value, free)
  return (
    <span className={`price ${className}`}>
      {price}
    </span>
)
}

Price.defaultProps = {
  className: '',
  free: 'Gratuit',
  value: null,
}

Price.propTypes = {
  className: PropTypes.string,
  free: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.array, PropTypes.number]),
}

export default Price
