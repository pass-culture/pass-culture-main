import React from 'react'
import moment from 'moment'

import BasicInput from './BasicInput'

const TimeInput = props => {
  const onInputChange = e => {
    const [hour, minutes] = e.target.value.split(':')
    console.log(props.value)
    const newTime = props.value //.clone()
    newTime.hours(hour)
    newTime.minutes(minutes)
    props.onChange({[props.dataKey]: newTime})
  }

  console.log(props.value)

  return <BasicInput {...props} onChange={onInputChange} value={props.value ? props.value.format(props.format) : ''} />
}

TimeInput.defaultProps = {
  format: 'HH:mm'
}

export default TimeInput
