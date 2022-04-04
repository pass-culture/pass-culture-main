import React from 'react'

import Select from 'components/layout/inputs/Select'
import { ALL_VENUES_OPTION, TPreFilters } from 'core/Bookings'

interface IFilterByVenueProps {
  isDisabled?: boolean
  selectedVenueId: string
  updateFilters: (filter: Partial<TPreFilters>) => void
  venuesFormattedAndOrdered: { displayName: string; id: string }[]
}

const FilterByVenue = ({
  isDisabled,
  updateFilters,
  selectedVenueId,
  venuesFormattedAndOrdered,
}: IFilterByVenueProps): JSX.Element => {
  function handleVenueSelection(event: React.ChangeEvent<HTMLSelectElement>) {
    const venueId = event.target.value
    updateFilters({ offerVenueId: venueId })
  }

  const venueOptions = venuesFormattedAndOrdered.map(venue => ({
    id: venue.id,
    displayName: venue.displayName,
  }))

  return (
    <Select
      defaultOption={ALL_VENUES_OPTION}
      handleSelection={handleVenueSelection}
      isDisabled={isDisabled}
      label="Lieu"
      name="lieu"
      options={venueOptions}
      selectedValue={selectedVenueId}
    />
  )
}

export default FilterByVenue
