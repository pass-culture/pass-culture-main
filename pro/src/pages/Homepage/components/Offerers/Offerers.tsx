import type { GetOffererResponseModel } from '@/apiClient/v1'
import type { SelectOption } from '@/commons/custom_types/form'
import { SoftDeletedOffererWarning } from '@/components/SoftDeletedOffererWarning/SoftDeletedOffererWarning'

import { OffererCreationLinks } from './components/OffererCreationLinks/OffererCreationLinks'
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
  const isOffererSoftDeleted = selectedOfferer && !selectedOfferer.isActive
  const userHasOfferers = offererOptions.length > 0
  const permanentVenues =
    selectedOfferer?.managedVenues?.filter((venue) => venue.isPermanent) ?? []

  return (
    <>
      {userHasOfferers && (
        <>
          {selectedOfferer && permanentVenues.length > 0 && (
            <PartnerPages venues={permanentVenues} offerer={selectedOfferer} />
          )}

          {selectedOfferer && !isOffererSoftDeleted && (
            <VenueList offerer={selectedOfferer} />
          )}
        </>
      )}
      {isOffererSoftDeleted && <SoftDeletedOffererWarning />}
      {!userHasOfferers && <OffererCreationLinks />}
    </>
  )
}
