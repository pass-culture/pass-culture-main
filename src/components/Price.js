import React from 'react'
import PropTypes from 'prop-types'

import { getPrice } from '../helpers'

const Price = ({ value, free, className }) => (
  <span className={`price ${className}`}>
    {getPrice(value, free)}
  </span>
)

Price.defaultProps = {
  className: '',
  free: 'Gratuit',
  value: null,
}

Price.propTypes = {
  className: PropTypes.string,
  free: PropTypes.string,
  value: PropTypes.number,
}

export default Price
