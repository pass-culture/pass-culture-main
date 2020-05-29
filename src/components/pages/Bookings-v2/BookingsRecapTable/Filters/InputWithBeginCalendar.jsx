import React from 'react'
import Icon from '../../../../layout/Icon'

export const InputWithBeginCalendar = inputProps => (
  <label className="flex-columns items-center field-input field-date field-date-begin">
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
