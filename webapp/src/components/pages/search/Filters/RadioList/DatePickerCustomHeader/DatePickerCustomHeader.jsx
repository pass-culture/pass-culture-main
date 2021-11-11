import PropTypes from 'prop-types'
import React from 'react'

import {
  FULL_MONTH_IN_LETTERS,
  LOCALE_FRANCE,
  YEAR_IN_NUMBER,
} from '../../../../../../utils/date/date'
import Icon from '../../../../../layout/Icon/Icon'

export const DatePickerCustomHeader = ({
  date,
  decreaseMonth,
  increaseMonth,
  nextMonthButtonDisabled,
  prevMonthButtonDisabled,
}) => {
  return (
    <div className="rl-datepicker-custom-header">
      <button
        disabled={prevMonthButtonDisabled}
        onClick={decreaseMonth}
        type="button"
      >
        <Icon
          alt="Aller au mois précédent"
          svg="ico-back-black"
        />
      </button>
      <span>
        {date
          .toDate()
          .toLocaleString(LOCALE_FRANCE, { ...YEAR_IN_NUMBER, ...FULL_MONTH_IN_LETTERS })}
      </span>
      <button
        disabled={nextMonthButtonDisabled}
        onClick={increaseMonth}
        type="button"
      >
        <Icon
          alt="Aller au mois suivant"
          svg="ico-next-black"
        />
      </button>
    </div>
  )
}

DatePickerCustomHeader.propTypes = {
  date: PropTypes.shape({
    toDate: PropTypes.func.isRequired,
  }).isRequired,
  decreaseMonth: PropTypes.func.isRequired,
  increaseMonth: PropTypes.func.isRequired,
  nextMonthButtonDisabled: PropTypes.bool.isRequired,
  prevMonthButtonDisabled: PropTypes.bool.isRequired,
}
