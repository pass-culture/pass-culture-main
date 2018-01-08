import React, { Component } from 'react'

import Select from './Select'

class OfferForm extends Component {
  constructor () {
    super()
  }
  render () {
    return (
      <div>
        <div className='mb1'>
        Which type is your offer?
        </div>
        <Select
          options={[
            { value: 'book', label: 'Book' },
            { value: 'theater', label: 'Theater' },
          ]}
        />
      </div>
    )
  }
}

export default OfferForm
