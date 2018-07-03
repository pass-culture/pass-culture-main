import moment from 'moment'
import React, { Component } from 'react'
import DatePicker from 'react-datepicker'
import { connect } from 'react-redux'

import { getFormValue, mergeForm } from '../../reducers/form'
import { NEW } from '../../utils/config'

class FormDate extends Component {

  handleDateSelect = date => {
    const {
      collectionName,
      entityId,
      mergeForm,
      name,
    } = this.props
    date && mergeForm(collectionName, entityId, name, date)
  }

  componentDidMount() {
    // fill automatically the form when it is a NEW POST action
    const { entityId, defaultValue } = this.props
    entityId === NEW && this.handleDateSelect(defaultValue)
  }

  componentDidUpdate (prevProps) {
    const {
      defaultValue,
      entityId
    } = this.props
    if (defaultValue && !defaultValue.isSame(prevProps.defaultValue, 'day')) {
      entityId === NEW && this.handleDateSelect(defaultValue)
    }
  }

  render () {
    const {
      format,
      highlightedDates,
      defaultValue,
      readOnly,
      showTimeSelect,
      value
    } = this.props
    const resolvedValue = value || defaultValue
    return (
      <div className="date-picker">
        {
          readOnly
            ? <span> {resolvedValue && resolvedValue.format(format)} </span>
            :
              (
                <DatePicker
                  selected={resolvedValue}
                  onChange={this.handleDateSelect}
                  className='input is-rounded is-small'
                  minDate={moment()}
                  highlightDates={highlightedDates || []}
                  showTimeSelect={showTimeSelect}
                />
            )
        }
      </div>
    )
  }
}

FormDate.defaultProps = {
  format: 'DD/MM/YYYY',
  entityId: NEW
}

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { mergeForm }
)(FormDate)
