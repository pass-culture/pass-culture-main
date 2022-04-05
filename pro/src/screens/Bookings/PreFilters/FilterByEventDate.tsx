import fr from 'date-fns/locale/fr'
import React from 'react'
import DatePicker, { registerLocale } from 'react-datepicker'

import InputWithCalendar from 'components/layout/inputs/PeriodSelector/InputWithCalendar'
import { DEFAULT_PRE_FILTERS, TPreFilters } from 'core/Bookings'
import { getToday } from 'utils/date'

registerLocale('fr', fr)

export interface IFilterByEventDateProps {
  isDisabled?: boolean
  selectedOfferDate: Date | string
  updateFilters: (filters: Partial<TPreFilters>) => void
}

const selectedOfferDateIsDate = (
  selectedOfferDate: Date | string
): selectedOfferDate is Date =>
  selectedOfferDate !== DEFAULT_PRE_FILTERS.offerEventDate

const FilterByEventDate = ({
  isDisabled = false,
  updateFilters,
  selectedOfferDate,
}: IFilterByEventDateProps): JSX.Element => {
  function handleOfferDateChange(offerEventDate: Date) {
    updateFilters({
      offerEventDate: offerEventDate
        ? offerEventDate
        : DEFAULT_PRE_FILTERS.offerEventDate,
    })
  }

  return (
    <div className="pf-offer-date">
      <label className="pf-offer-date-label" htmlFor="select-filter-date">
        Date de l’évènement
      </label>
      <div className="pf-offer-date-picker">
        <DatePicker
          className="pf-offer-date-input"
          customInput={
            <InputWithCalendar
              // @ts-expect-error InputWithCalendar should be rewritten in ts
              customClass={`field-date-only${isDisabled ? ' disabled' : ''}`}
            />
          }
          dateFormat="dd/MM/yyyy"
          disabled={isDisabled}
          dropdownMode="select"
          id="select-filter-date"
          locale="fr"
          onChange={handleOfferDateChange}
          openToDate={
            selectedOfferDateIsDate(selectedOfferDate)
              ? selectedOfferDate
              : getToday()
          }
          placeholderText="JJ/MM/AAAA"
          selected={
            selectedOfferDateIsDate(selectedOfferDate)
              ? selectedOfferDate
              : null
          }
        />
      </div>
    </div>
  )
}

export default FilterByEventDate
