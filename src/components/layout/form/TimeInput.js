import React, { Component } from 'react'
import moment from 'moment'

import BasicInput from './BasicInput'

class TimeInput extends Component {

  onInputChange = e => {
    const { onChange, value } = this.props
    if (onChange && value) {
      // console.log('value', value)
      const [hour, minutes] = e.target.value.split(':')
      // console.log('hour, minutes', hour, minutes)
      const date = moment(value)
        .hours(hour)
        .minutes(minutes)
      onChange(date && date.toISOString())
    }
  }

  render () {
    const { value, tz } = this.props

    //console.log('value', value, moment(value).tz(tz))
    return (
      <BasicInput {...this.props}
        onChange={this.onInputChange}
        value={
          value && moment(value).tz(tz)
            ? moment(value).tz(tz).format('HH:mm')
            : ''
        }
      />
    )
  }
}

export default TimeInput
