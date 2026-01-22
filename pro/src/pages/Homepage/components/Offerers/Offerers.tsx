import type { GetOffererResponseModel } from '@/apiClient/v1'
import type { SelectOption } from '@/commons/custom_types/form'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { SoftDeletedOffererWarning } from '@/components/SoftDeletedOffererWarning/SoftDeletedOffererWarning'

import { OffererCreationLinks } from './components/OffererCreationLinks/OffererCreationLinks'
import { PartnerPage } from './components/PartnerPages/components/PartnerPage'
import { PartnerPages } from './components/PartnerPages/PartnerPages'
import { VenueList } from './components/VenueList/VenueList'

export interface OfferersProps {
  selectedOfferer: GetOffererResponseModel | null
  offererOptions: SelectOption[]
}

export const Offerers = ({
  offererOptions,
  selectedOfferer,
}: OfferersProps) => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')

  const selectedVenue = useAppSelector((store) => store.user.selectedVenue)

  const isOffererSoftDeleted = selectedOfferer && !selectedOfferer.isActive
  const userHasOfferers = offererOptions.length > 0
  const permanentVenues = selectedOfferer?.managedVenues ?? []

  return (
    <>
      {!withSwitchVenueFeature && userHasOfferers && (
        <>
          {selectedOfferer && permanentVenues.length > 0 && (
            <PartnerPages venues={permanentVenues} offerer={selectedOfferer} />
          )}
          {selectedOfferer && !isOffererSoftDeleted && (
            <VenueList offerer={selectedOfferer} />
          )}
        </>
      )}
      {withSwitchVenueFeature && selectedOfferer && selectedVenue && (
        <PartnerPage
          offerer={selectedOfferer}
          venue={selectedVenue}
          venueHasPartnerPage={selectedVenue.hasPartnerPage}
        />
      )}
      {isOffererSoftDeleted && <SoftDeletedOffererWarning />}
      {!userHasOfferers && <OffererCreationLinks />}
    </>
  )
}
