import React, { Component } from 'react'
import { connect } from 'react-redux'

import Select from './Select'
import BookForm from '../forms/BookForm'
import { assignForm } from '../reducers/form'
import { getCurrentWork } from '../reducers/request'

class OfferForm extends Component {
  componentWillReceiveProps (nextProps) {
    const { assignForm, work } = nextProps
    if (work && work !== this.props.work) {
      assignForm({ workId: work.id })
    }
  }
  onOptionClick = ({ target: { value } }) => {
    this.props.assignForm({ category: value })
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

export default connect(state => {
  const { form: { category } } = state
  return { category,
    work: getCurrentWork(state)
  }
}, { assignForm })(OfferForm)
