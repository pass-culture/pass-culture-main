import React, { Component } from 'react'

import FormInput from './FormInput'

class PriceItem extends Component {
  render () {
    const { endDate, startDate, size, value } = this.props
    return (
      <div className='price-item mb3 col-9 mx-auto p2'>

        <label className='mr1'>
          début
        </label>
        {startDate}
        <br />

        <label className='mr1'>
          fin
        </label>
        {endDate}
        <br />

        <label className='mr1'>
          groupe
        </label>
        {size}
        <br />

        <label className='mr1'>
          prix
        </label>
        {value}
      </div>
    )
  }
}

export default PriceItem
