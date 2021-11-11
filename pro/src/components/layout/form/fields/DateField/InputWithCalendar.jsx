/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import React from 'react'

import Icon from '../../../Icon'

export const InputWithCalendar = inputProps => (
  <label className="flex-columns items-center field-input field-date">
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
