import React from 'react'

const Price = ({ value, free, Tag, className }) => {
  return (
    <Tag className={['price'].concat(className).join(' ')}>
      {typeof value === 'undefined'
        ? ''
        : value === 0
          ? free
          : value && value.toString().replace('.', ',') + '€'}
    </Tag>
  )
}

Price.defaultProps = {
  free: 'Gratuit',
  Tag: 'span',
}

export default Price
