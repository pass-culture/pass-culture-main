import React from 'react'

const Price = ({ value }) => {
  return (
    <div className='price'>{
      value === 0
        ? 'gratuit'
        : value && (value.toString().replace('.', ',')+'€')
    }</div>
  )
}

export default Price;
