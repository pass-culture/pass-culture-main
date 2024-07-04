import isEqual from 'lodash.isequal'
import React, { useState } from 'react'

import { ALL_VENUES_OPTION } from 'core/Bookings/constants'
import { PreFiltersParams } from 'core/Bookings/types'
import { useIsNewInterfaceActive } from 'hooks/useIsNewInterfaceActive'
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
  const isNewSideNavActive = useIsNewInterfaceActive()
  const [previousVenues, setPreviousVenues] = useState(
    venuesFormattedAndOrdered
  )

  if (
    isNewSideNavActive &&
    venuesFormattedAndOrdered.length &&
    !isEqual(venuesFormattedAndOrdered, previousVenues)
  ) {
    if (previousVenues.length) {
      setTimeout(() => {
        updateFilters({ offerVenueId: venuesFormattedAndOrdered[0]?.id })
      })
    }
    setPreviousVenues(venuesFormattedAndOrdered)
  }

  return (
    <FieldLayout
      label="Lieu"
      name="lieu"
      className={styles['venue-filter']}
      isOptional
    >
      <SelectInput
        defaultOption={isNewSideNavActive ? null : ALL_VENUES_OPTION}
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
