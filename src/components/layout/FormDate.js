import moment from 'moment'
import React, { Component } from 'react'
import { SingleDatePicker } from 'react-dates'
import { connect } from 'react-redux'

import Icon from './Icon'
import { getFormValue, mergeForm } from '../../reducers/form'

class FormDate extends Component {

  constructor () {
    super()
    this.state = {
      focused: false
    }
  }

  handleDateSelect = () => {
    const {
      collectionName,
      entityId,
      mergeForm,
      name,
      value
    } = this.props

    /*
    // build the datetime based on the date plus the time
    // given in the horaire form field
    if (!newDate || !newDate.time || !newOffer) {
      return this.setState({ withError: true })
    }
    const [hours, minutes] = newDate.time.split(':')
    const datetime = date.clone().hour(hours).minute(minutes)

    // check that it does not match already an occurence
    const alreadySelectedOccurence = occurences && occurences.find(o =>
      o.beginningDatetimeMoment.isSame(datetime))
    if (alreadySelectedOccurence) {
      return
    }
    */
    mergeForm(collectionName, entityId, name, value)
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
          initialVisibleMonth={() => moment.min(availableDates)}
          inputIconPosition="after"
          isDayBlocked={date =>
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

export default connect(
  (state, ownProps) => ({ value: getFormValue(state, ownProps) }),
  { mergeForm }
)(FormDate)
