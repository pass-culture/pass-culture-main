import React from 'react'

const Price = ({ value, free, Tag, className }) => {
  value = value || 0;
  return (
    <Tag className={['price'].concat(className).join(' ')}>{
      value === 0
        ? free
        : value && (value.toString().replace('.', ',')+'€')
    }</Tag>
  )
}

Price.defaultProps = {
  free: 'gratuit',
  Tag: 'span',
}

export default Price;
