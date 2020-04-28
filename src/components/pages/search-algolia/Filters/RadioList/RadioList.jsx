import moment from 'moment'
import PropTypes from 'prop-types'
import React, { forwardRef } from 'react'
import DatePicker from 'react-datepicker'

import { DatePickerCustomHeader } from '../DatePicker/DatePickerCustomHeader'
import { DATE_FILTER } from '../filtersEnums'
import { Radio } from './Radio/Radio'

export const RadioList = forwardRef(function RadioList(
  { date, onDateSelection, onPickedDate },
  ref
) {
  return (
    <li
      className="rl-date-wrapper"
      ref={date.option !== DATE_FILTER.USER_PICK.value ? ref : undefined}
    >
      <h4 className="sf-title">
        {"Date de l'offre"}
      </h4>
      <ul>
        {Object.keys(DATE_FILTER).map(dateFilterOption => (
          <div
            key={DATE_FILTER[dateFilterOption].id}
            ref={
              DATE_FILTER[dateFilterOption].value === DATE_FILTER.USER_PICK.value &&
              date.option === DATE_FILTER.USER_PICK.value
                ? ref
                : undefined
            }
          >
            <Radio
              onDateSelection={onDateSelection}
              option={DATE_FILTER[dateFilterOption]}
              selectedDateOption={date.option}
            />
          </div>
        ))}
      </ul>
      {date.option === DATE_FILTER.USER_PICK.value && (
        <DatePicker
          calendarClassName="rl-filter-datepicker"
          inline
          minDate={moment(new Date())}
          onChange={onPickedDate}
          renderCustomHeader={DatePickerCustomHeader}
          selected={moment(date.selectedDate)}
        />
      )}
    </li>
  )
})

RadioList.propTypes = {
  date: PropTypes.shape({ option: PropTypes.string, selectedDate: PropTypes.instanceOf(Date) })
    .isRequired,
  onDateSelection: PropTypes.func.isRequired,
  onPickedDate: PropTypes.func.isRequired,
}
