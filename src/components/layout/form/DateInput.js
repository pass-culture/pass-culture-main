import React from 'react'
import DatePicker from 'react-datepicker'
import moment from 'moment'

import Icon from '../Icon'

const DateInput = props => {

  const onChange = date => {
    props.onChange({[props.name]: date})
  }

  return props.readOnly ? (
    <span> {props.value && props.value.format(props.dateFormat)} </span>
    ) : (
    <div className={`input is-${props.size} date-picker`}>
      <span>
        <DatePicker
          className='date'
          filterDate={props.filterDate}
          highlightDates={props.highlightedDates || []}
          minDate={props.minDate || moment()}
          onChange={onChange}
          readOnly={props.readOnly}
          selected={props.value ? moment(props.value) : null}
        />
      </span>
      <span className='icon'>
        <Icon
          alt='Horaires'
          className="input-icon"
          svg="ico-calendar"
        />
      </span>
    </div>
  )
}

DateInput.defaultProps = {
  dateFormat: 'DD/MM/YYYY',
}

export default DateInput

