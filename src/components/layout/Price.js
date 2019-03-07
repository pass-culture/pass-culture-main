import React from 'react'
import PropTypes from 'prop-types'

import { getPrice } from '../../helpers'

const Price = ({ free, value, ...rest }) => {
  const price = getPrice(value, free)
  return (
    <span {...rest} className="price">
      {price}
    </span>
  )
}

Price.defaultProps = {
  free: null,
  value: null,
}

Price.propTypes = {
  free: PropTypes.string,
  value: PropTypes.oneOfType([PropTypes.array, PropTypes.number]),
}

export default Price
