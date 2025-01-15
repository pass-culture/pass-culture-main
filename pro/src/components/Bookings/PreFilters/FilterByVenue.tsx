import {
  ALL_STRUCTURES_OPTION,
  ALL_VENUES_OPTION,
} from 'commons/core/Bookings/constants'
import { PreFiltersParams } from 'commons/core/Bookings/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
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

  const isOfferAddressEnabled = useActiveFeature('WIP_ENABLE_OFFER_ADDRESS')

  return (
    <FieldLayout
      label={isOfferAddressEnabled ? 'Structure' : 'Lieu'}
      name="lieu"
      className={styles['venue-filter']}
      isOptional
    >
      <SelectInput
        defaultOption={
          isOfferAddressEnabled ? ALL_STRUCTURES_OPTION : ALL_VENUES_OPTION
        }
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
