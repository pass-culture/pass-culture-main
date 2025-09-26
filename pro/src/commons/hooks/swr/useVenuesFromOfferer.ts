import { formatAndOrderVenues } from 'repository/venuesService'

import { useOfferer } from '@/commons/hooks/swr/useOfferer'
import { getPhysicalVenuesFromOfferer } from '@/pages/Homepage/components/Offerers/components/VenueList/venueUtils'

export const useVenuesFromOfferer = (
  selectedOffererId: number | null,
  useFallbackData?: boolean
) => {
  const { data: selectedOfferer, ...rest } = useOfferer(
    selectedOffererId,
    useFallbackData
  )

  const physicalVenues = getPhysicalVenuesFromOfferer(selectedOfferer)
  const rawVenues = [...physicalVenues].filter((v) => !!v)
  const data = formatAndOrderVenues(rawVenues)

  return {
    selectedOffererId,
    data,
    ...rest,
  }
}
