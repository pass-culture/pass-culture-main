import React from 'react'

import { DEFAULT_PRE_FILTERS, TPreFilters } from 'core/Bookings'
import { BaseDatePicker } from 'ui-kit/form/DatePicker/BaseDatePicker'
import { FieldLayout } from 'ui-kit/form/shared'

import styles from './PreFilters.module.scss'

export interface FilterByEventDateProps {
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
}: FilterByEventDateProps): JSX.Element => (
  <FieldLayout
    label="Date de l’évènement"
    name="select-filter-date"
    className={styles['offer-date-filter']}
  >
    <BaseDatePicker
      name="select-filter-date"
      onChange={(date: Date) =>
        updateFilters({
          offerEventDate: date ? date : DEFAULT_PRE_FILTERS.offerEventDate,
        })
      }
      disabled={isDisabled}
      value={
        selectedOfferDateIsDate(selectedOfferDate) ? selectedOfferDate : null
      }
    />
  </FieldLayout>
)

export default FilterByEventDate
