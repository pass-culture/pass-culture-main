import { useOfferer } from 'commons/hooks/swr/useOfferer'
import {
  getPhysicalVenuesFromOfferer,
  getVirtualVenueFromOfferer,
} from 'pages/Homepage/components/Offerers/components/VenueList/venueUtils'
import { formatAndOrderVenues } from 'repository/venuesService'

export const useVenuesFromOfferer = (
  selectedOffererId: number | null,
  useFallbackData?: boolean
) => {
  const { data: selectedOfferer, ...rest } = useOfferer(
    selectedOffererId,
    useFallbackData
  )

  const physicalVenues = getPhysicalVenuesFromOfferer(selectedOfferer)
  const virtualVenue = getVirtualVenueFromOfferer(selectedOfferer)
  const rawVenues = [...physicalVenues, virtualVenue].filter((v) => !!v)
  const data = formatAndOrderVenues(rawVenues)

  return {
    selectedOffererId,
    data,
    ...rest,
  }
}
