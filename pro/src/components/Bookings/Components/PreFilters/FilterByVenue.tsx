import { ALL_STRUCTURES_OPTION } from '@/commons/core/Bookings/constants'
import type { PreFiltersParams } from '@/commons/core/Bookings/types'
import { SelectInput } from '@/ui-kit/form/shared/BaseSelectInput/SelectInput'
import { FieldLayout } from '@/ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from './PreFilters.module.scss'

interface FilterByVenueProps {
  isDisabled?: boolean
  selectedVenueId: string
  updateFilters: (filter: Partial<PreFiltersParams>) => void
  venuesFormattedAndOrdered: { label: string; value: string }[]
}

export const FilterByVenue = ({
  isDisabled,
  updateFilters,
  selectedVenueId,
  venuesFormattedAndOrdered,
}: FilterByVenueProps): JSX.Element => {
  return (
    <FieldLayout
      label="Structure"
      name="lieu"
      className={styles['venue-filter']}
      required={false}
    >
      <SelectInput
        defaultOption={ALL_STRUCTURES_OPTION}
        onChange={(event) =>
          updateFilters({ offerVenueId: event.target.value })
        }
        disabled={isDisabled}
        name="lieu"
        options={venuesFormattedAndOrdered}
        value={selectedVenueId}
      />
    </FieldLayout>
  )
}
