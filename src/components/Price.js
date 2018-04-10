import React from 'react'

const Price = (({value}) => {
  return (
    <span className='price'>{value == 0 ? 'gratuit' : value.toString().replace('.', ',')+'€'}</span>
  )
})

export default Price;
