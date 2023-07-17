import React from 'react'

import { DEFAULT_PRE_FILTERS } from 'core/Bookings/constants'
import { PreFiltersParams } from 'core/Bookings/types'
import { BaseDatePicker } from 'ui-kit/form/DatePicker/BaseDatePicker'
import { FieldLayout } from 'ui-kit/form/shared'
import { isDateValid } from 'utils/date'

import styles from './PreFilters.module.scss'

export interface FilterByEventDateProps {
  isDisabled?: boolean
  selectedOfferDate: string
  updateFilters: (filters: Partial<PreFiltersParams>) => void
}

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
      onChange={event =>
        updateFilters({
          offerEventDate:
            event.target.value !== ''
              ? event.target.value
              : DEFAULT_PRE_FILTERS.offerEventDate,
        })
      }
      disabled={isDisabled}
      value={isDateValid(selectedOfferDate) ? selectedOfferDate : ''}
    />
  </FieldLayout>
)

export default FilterByEventDate
