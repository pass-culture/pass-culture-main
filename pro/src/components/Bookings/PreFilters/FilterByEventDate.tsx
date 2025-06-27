import { DEFAULT_PRE_FILTERS } from 'commons/core/Bookings/constants'
import { PreFiltersParams } from 'commons/core/Bookings/types'
import { isDateValid } from 'commons/utils/date'
import { BaseDatePicker } from 'ui-kit/form/shared/BaseDatePicker/BaseDatePicker'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from './PreFilters.module.scss'

export interface FilterByEventDateProps {
  isDisabled?: boolean
  selectedOfferDate: string
  updateFilters: (filters: Partial<PreFiltersParams>) => void
}

export const FilterByEventDate = ({
  isDisabled = false,
  updateFilters,
  selectedOfferDate,
}: FilterByEventDateProps): JSX.Element => (
  <FieldLayout
    label="Date de l’évènement"
    name="select-filter-date"
    className={styles['offer-date-filter']}
    isOptional
  >
    <BaseDatePicker
      name="select-filter-date"
      onChange={(event) =>
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
