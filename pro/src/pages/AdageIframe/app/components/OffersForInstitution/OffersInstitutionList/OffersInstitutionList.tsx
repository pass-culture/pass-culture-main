import React from 'react'

import { VenueResponse } from 'apiClient/adage'
import useAdageUser from 'pages/AdageIframe/app/hooks/useAdageUser'

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
  const adageUser = useAdageUser()
  return (
    <Offers
      setIsLoading={() => {}}
      userRole={adageUser.role}
      userEmail={adageUser.email}
      displayStats={false}
    />
  )
}
export default OffersInstitutionList
