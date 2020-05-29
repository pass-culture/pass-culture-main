import React from 'react'
import Icon from '../../../../layout/Icon'

export const InputWithEndCalendar = inputProps => (
  <label className="flex-columns items-center field-input field-date field-date-end">
    <input
      type="text"
      {...inputProps}
    />
    <div className="flex-auto" />
    <Icon
      alt="Horaires"
      svg="ico-calendar"
    />
  </label>
)
