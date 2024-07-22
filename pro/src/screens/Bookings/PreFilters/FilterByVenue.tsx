import React from 'react'

import { ALL_VENUES_OPTION } from 'core/Bookings/constants'
import { PreFiltersParams } from 'core/Bookings/types'
import { SelectInput } from 'ui-kit/form/Select/SelectInput'
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
      label="Lieu"
      name="lieu"
      className={styles['venue-filter']}
      isOptional
    >
      <SelectInput
        defaultOption={ALL_VENUES_OPTION}
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
