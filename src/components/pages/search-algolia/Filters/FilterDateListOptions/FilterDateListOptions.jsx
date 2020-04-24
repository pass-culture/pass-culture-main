import React from 'react'
import moment from 'moment'
import PropTypes from 'prop-types'
import DatePicker from 'react-datepicker'
import { DATE_FILTER } from '../filtersEnums'
import { FilterDateListOption } from './FilterDateListOption'


export function FilterDateListOptions({ date, onDateSelection, onPickedDate }) {
  return (
    <li className="sf-date-wrapper">
      <h4 className="sf-title">
        {"Date de l'offre"}
      </h4>
      <ul>
        {Object.keys(DATE_FILTER).map(dateFilterOption => {
          return (
            <FilterDateListOption
              key={dateFilterOption.value}
              onDateSelection={onDateSelection}
              option={DATE_FILTER[dateFilterOption]}
              selectedDateOption={date.option}
            />)
        })}
      </ul>
      {date.option === DATE_FILTER.USER_PICK.value && (
        <DatePicker
          calendarClassName="sf-filter-datepicker"
          dropdownMode="select"
          inline
          minDate={moment(new Date())}
          onChange={onPickedDate}
          selected={moment(date.selectedDate)}
        />
      )}
    </li>)
}

FilterDateListOptions.propTypes = {
  date: PropTypes.shape({ option: PropTypes.string, selectedDate: PropTypes.instanceOf(Date) }).isRequired,
  onDateSelection: PropTypes.func.isRequired,
  onPickedDate: PropTypes.func.isRequired,
}
