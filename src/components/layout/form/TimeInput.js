import React from 'react'
import moment from 'moment'

import BasicInput from './BasicInput'

const TimeInput = props => {
  const onInputChange = e => props.onChange(e.target.value)

  return <BasicInput {...props} onChange={onInputChange} value={props.value ? moment(props.value).format(props.format) : ''} />
}

TimeInput.defaultProps = {
  format: 'HH:mm'
}

export default TimeInput
