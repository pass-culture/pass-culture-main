import type {
  GetOffererResponseModel,
  VenueTypeResponseModel,
} from '@/apiClient/v1'
import type { SelectOption } from '@/commons/custom_types/form'
import { Card } from '@/components/Card/Card'
import { SoftDeletedOffererWarning } from '@/components/SoftDeletedOffererWarning/SoftDeletedOffererWarning'
import { Spinner } from '@/ui-kit/Spinner/Spinner'

import { OffererCreationLinks } from './components/OffererCreationLinks/OffererCreationLinks'
import { PartnerPages } from './components/PartnerPages/PartnerPages'
import { VenueList } from './components/VenueList/VenueList'
import styles from './Offerers.module.scss'

export interface OfferersProps {
  selectedOfferer: GetOffererResponseModel | null
  isLoading: boolean
  isUserOffererValidated: boolean
  offererOptions: SelectOption[]
  venueTypes: VenueTypeResponseModel[]
}

export const Offerers = ({
  offererOptions,
  selectedOfferer,
  isLoading,
  isUserOffererValidated,
  venueTypes,
}: OfferersProps) => {
  if (isLoading) {
    return (
      <Card>
        <div className={styles['loader-container']}>
          <Spinner />
        </div>
      </Card>
    )
  }

  const isOffererSoftDeleted = selectedOfferer && !selectedOfferer.isActive
  const userHasOfferers = offererOptions.length > 0
  const permanentVenues =
    selectedOfferer?.managedVenues?.filter((venue) => venue.isPermanent) ?? []

  return (
    <>
      {userHasOfferers && (
        <>
          {selectedOfferer && permanentVenues.length > 0 && (
            <PartnerPages
              venues={permanentVenues}
              offerer={selectedOfferer}
              venueTypes={venueTypes}
            />
          )}

          {selectedOfferer && !isOffererSoftDeleted && (
            <VenueList offerer={selectedOfferer} />
          )}
        </>
      )}
      {
        /* istanbul ignore next: DEBT, TO FIX */ isUserOffererValidated &&
          isOffererSoftDeleted && <SoftDeletedOffererWarning />
      }
      {!userHasOfferers && <OffererCreationLinks />}
    </>
  )
}
