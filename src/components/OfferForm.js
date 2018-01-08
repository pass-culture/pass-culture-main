import React, { Component } from 'react'
import { connect } from 'react-redux'

import Select from './Select'
import BookForm from '../forms/BookForm'

class OfferForm extends Component {
  constructor () {
    super()
    this.state = { selectedType: null }
    this.onOptionClick = this._onOptionClick.bind(this)
  }
  _onOptionClick ({ target: { value } }) {
    this.setState({ selectedType: value })

  }
  render () {
    const { options } = this.props
    const { selectedType } = this.state
    return (
      <div className='offer-form'>
        <Select className='select mb2'
          defaultLabel='-- select a type --'
          onOptionClick={this.onOptionClick}
          options={options}
        />
        { selectedType === 'book' && <BookForm /> }
      </div>
    )
  }
}

OfferForm.defaultProps = {
  options: [
    { value: 'book', label: 'Book' },
    { value: 'theater', label: 'Theater' }
  ]
}


export default connect()(OfferForm)
