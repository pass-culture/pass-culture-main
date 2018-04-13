import React from 'react'

const Price = ({ value, free, Tag, className }) => {
  return (
    <Tag className={className}>{
      value === 0
        ? free
        : value && (value.toString().replace('.', ',')+'€')
    }</Tag>
  )
}

Price.defaultProps = {
  free: 'gratuit',
  Tag: 'span',
  className: 'price',
}

export default Price;
