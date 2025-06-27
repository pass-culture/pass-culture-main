import { ALL_STRUCTURES_OPTION } from 'commons/core/Bookings/constants'
import { PreFiltersParams } from 'commons/core/Bookings/types'
import { SelectInput } from 'ui-kit/form/shared/BaseSelectInput/SelectInput'
import { FieldLayout } from 'ui-kit/form/shared/FieldLayout/FieldLayout'

import styles from './PreFilters.module.scss'

interface FilterByVenueProps {
  isDisabled?: boolean
  selectedVenueId: string
  updateFilters: (filter: Partial<PreFiltersParams>) => void
  venuesFormattedAndOrdered: { displayName: string; id: string }[]
}

export const FilterByVenue = ({
  isDisabled,
  updateFilters,
  selectedVenueId,
  venuesFormattedAndOrdered,
}: FilterByVenueProps): JSX.Element => {
  const venueOptions = venuesFormattedAndOrdered.map((venue) => ({
    value: venue.id,
    label: venue.displayName,
  }))

  return (
    <FieldLayout
      label="Structure"
      name="lieu"
      className={styles['venue-filter']}
      isOptional
    >
      <SelectInput
        defaultOption={ALL_STRUCTURES_OPTION}
        onChange={(event) =>
          updateFilters({ offerVenueId: event.target.value })
        }
        disabled={isDisabled}
        name="lieu"
        options={venueOptions}
        value={selectedVenueId}
      />
    </FieldLayout>
  )
}
