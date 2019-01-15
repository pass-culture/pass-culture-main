import React from 'react'
import PropTypes from 'prop-types'

import { getPrice } from '../../helpers'

const Price = ({ value }) => {
  const price = getPrice(value)
  return (
    <span className="price">
      {price}
    </span>
)
}

Price.defaultProps = {
  value: null,
}

Price.propTypes = {
  value: PropTypes.oneOfType([PropTypes.array, PropTypes.number]),
}

export default Price
