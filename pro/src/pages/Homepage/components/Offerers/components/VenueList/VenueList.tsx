import type { GetOffererResponseModel } from '@/apiClient/v1'
import { getPhysicalVenuesFromOfferer } from '@/pages/Homepage/components/Offerers/components/VenueList/venueUtils'

import { Venue } from './Venue'
import styles from './Venue.module.scss'

export interface VenueListProps {
  offerer: GetOffererResponseModel
}

export const VenueList = ({ offerer }: VenueListProps) => {
  const basePhysicalVenues = getPhysicalVenuesFromOfferer(offerer)

  const physicalVenues = basePhysicalVenues.filter(
    (venue) => !venue.isPermanent
  )

  const indexLastPhysicalVenues = physicalVenues.length - 1

  return (
    <div className={styles['venue-list']}>
      {physicalVenues.map((venue, index) => (
        <Venue
          key={`${offerer.id}-${venue.id}`}
          venue={venue}
          offerer={offerer}
          isFirstVenue={index === indexLastPhysicalVenues}
        />
      ))}
    </div>
  )
}
