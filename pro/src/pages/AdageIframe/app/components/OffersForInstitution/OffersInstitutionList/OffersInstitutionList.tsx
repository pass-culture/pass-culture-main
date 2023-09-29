import React from 'react'

import { VenueResponse } from 'apiClient/adage'

import { Offers } from '../../OffersInstantSearch/OffersSearch/Offers/Offers'

interface OffersInstitutionListProps {
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}
/* eslint-disable @typescript-eslint/no-unused-vars */
const OffersInstitutionList = ({
  removeVenueFilter,
  venueFilter,
}: OffersInstitutionListProps): JSX.Element => {
  return <Offers displayStats={false} />
}
export default OffersInstitutionList
