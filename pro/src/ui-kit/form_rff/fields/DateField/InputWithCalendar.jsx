import React from 'react'

import Icon from 'ui-kit/Icon/Icon'

export const InputWithCalendar = inputProps => (
  <label className="flex-columns items-center field-input field-date">
    <input type="text" {...inputProps} />
    <div className="flex-auto" />
    <Icon alt="Horaires" svg="ico-calendar" />
  </label>
)
