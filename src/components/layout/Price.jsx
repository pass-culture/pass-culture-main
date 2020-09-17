import PropTypes from 'prop-types'
import React from 'react'

const Price = ({ value, free, Tag, className }) => {
  return (
    <Tag className={['price'].concat(className).join(' ')}>
      {typeof value === 'undefined'
        ? ''
        : value === 0
          ? free
          : value && value.toString().replace('.', ',') + ' €'}
    </Tag>
  )
}

Price.defaultProps = {
  Tag: 'span',
  className: null,
  free: 'Gratuit',
}

Price.propTypes = {
  Tag: PropTypes.string,
  className: PropTypes.string,
  free: PropTypes.string,
  value: PropTypes.number.isRequired,
}

export default Price
