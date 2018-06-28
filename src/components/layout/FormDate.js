import moment from 'moment'
import React, { Component } from 'react'
import DatePicker from 'react-datepicker'
import { connect } from 'react-redux'

import Icon from './Icon'
import { getFormValue, mergeForm } from '../../reducers/form'
import { NEW } from '../../utils/config'

class FormDate extends Component {

  constructor () {
    super()
    this.state = {
      focused: false
    }
  }

  handleDateSelect = date => {
    const {
      collectionName,
      entityId,
      mergeForm,
      name,
    } = this.props
    mergeForm(collectionName, entityId, name, date)
  }

  render () {
    const {
      availableDates,
      highlightedDates,
      defaultValue,
      value
    } = this.props
    const { focused } = this.state
    console.log('')
    return (
      <div className="input-field date-picker">
        <DatePicker
          selected={value || defaultValue}
          onChange={this.handleDateSelect}
          className='input is-rounded is-small'
          minDate={moment()}
          highlightDates={highlightedDates || []}
        />
      </div>
    )
  }
}

FormDate.defaultProps = {
  entityId: NEW
}

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { mergeForm }
)(FormDate)
