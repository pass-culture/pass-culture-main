import React, { Component } from 'react'
import moment from 'moment'

import BasicInput from './BasicInput'

class TimeInput extends Component {

  onInputChange = e => {
    const { onChange, value } = this.props
    if (onChange && value) {
      const [hour, minutes] = e.target.value.split(':')
      onChange(
        moment(value)
          .hours(hour)
          .minutes(minutes)
          .toISOString()
      )
    }
  }

  render () {
    const { value, tz } = this.props
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
