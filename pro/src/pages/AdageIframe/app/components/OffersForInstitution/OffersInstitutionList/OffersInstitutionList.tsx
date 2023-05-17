import React from 'react'

import { AuthenticatedResponse, VenueResponse } from 'apiClient/adage'

import { Offers } from '../../OffersInstantSearch/OffersSearch/Offers/Offers'

interface OffersInstitutionListProps {
  user: AuthenticatedResponse
  removeVenueFilter: () => void
  venueFilter: VenueResponse | null
}
/* eslint-disable @typescript-eslint/no-unused-vars */
const OffersInstitutionList = ({
  user,
  removeVenueFilter,
  venueFilter,
}: OffersInstitutionListProps): JSX.Element => {
  return (
    <Offers
      setIsLoading={() => {}}
      userRole={user.role}
      userEmail={user.email}
      displayStats={false}
    />
  )
}
export default OffersInstitutionList
