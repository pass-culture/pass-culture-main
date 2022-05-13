import Icon from '../../../Icon'
import React from 'react'

export const InputWithCalendar = inputProps => (
  <label className="flex-columns items-center field-input field-date">
    <input type="text" {...inputProps} />
    <div className="flex-auto" />
    <Icon alt="Horaires" svg="ico-calendar" />
  </label>
)
