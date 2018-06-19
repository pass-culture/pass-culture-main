import moment from 'moment'
import React, { Component } from 'react'
import { SingleDatePicker } from 'react-dates'
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
      availableDates,
      collectionName,
      entityId,
      mergeForm,
      name,
    } = this.props
    mergeForm(collectionName, entityId, name, date)
  }

  render () {
    const { availableDates, value } = this.props
    const { focused } = this.state
    return (
      <div className="input-field date-picker">
        <SingleDatePicker
          customInputIcon={<Icon svg="ico-calendar" alt="calendrier" />}
          customCloseIcon={<Icon svg='ico-close-b' alt="Fermer" />}
          date={value}
          displayFormat="LL"
          focused={focused}
          initialVisibleMonth={() => moment.min(availableDates || [])}
          inputIconPosition="after"
          isDayBlocked={date => date && availableDates &&
            !availableDates.find(d => d.isSame(date, 'day'))
          }
          noBorder={true}
          numberOfMonths={1}
          onDateChange={this.handleDateSelect}
          onFocusChange={({ focused }) => this.setState({ focused })}
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
