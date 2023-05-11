import React from 'react'

import { AuthenticatedResponse, VenueResponse } from 'apiClient/adage'

interface OffersInstitutionList {
  user: AuthenticatedResponse
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}
/* eslint-disable @typescript-eslint/no-unused-vars */
// FIX ME : Will be implemented in a future PR
const OffersInstitutionList = ({
  user,
  removeVenueFilter,
  venueFilter,
}: OffersInstitutionList): JSX.Element => {
  //FIX ME : to implement
  return <div>Offres pour mon établissement</div>
}
export default OffersInstitutionList
