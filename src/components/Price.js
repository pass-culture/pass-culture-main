import React from 'react'

const Price = (({value}) => {
  return (
    <span className='price'>{value.toString().replace('.', ',')}€</span>
  )
})

export default Price;