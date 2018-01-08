import React, { Component } from 'react'
import { connect } from 'react-redux'

import Select from './Select'
import BookForm from '../forms/BookForm'
import { setFormCategory } from '../reducers/form'

class OfferForm extends Component {
  constructor () {
    super()
    this.onOptionClick = this._onOptionClick.bind(this)
  }
  _onOptionClick ({ target: { value } }) {
    this.props.setFormCategory(value)
  }
  render () {
    const { category, options } = this.props
    return (
      <div className='offer-form'>
        <Select className='select mb2'
          defaultLabel='-- select a type --'
          onOptionClick={this.onOptionClick}
          options={options}
          value={category}
        />
        { category === 'book' && <BookForm /> }
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

export default connect(({ form: { category } }) =>
  ({ category }), { setFormCategory })(OfferForm)
