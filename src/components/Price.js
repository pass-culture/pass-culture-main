import React from 'react'
import PropTypes from 'prop-types'

const Price = ({ value, free, className }) => {
  let price =
    typeof value === 'undefined'
      ? ''
      : value === 0
        ? free
        : value && `${value.toString().replace('.', ',')}€`
  if (price === 0) price = free
  else price = value && `${value.toString().replace('.', ',')}€`
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
  value: PropTypes.number,
}

export default Price
