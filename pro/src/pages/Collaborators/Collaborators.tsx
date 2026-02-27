import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureOffererNames } from '@/commons/store/offerer/selectors'
import { isSelectedVenueAssociated } from '@/commons/store/user/selectors'
import { NonAttachedBanner } from '@/components/NonAttachedBanner/NonAttachedBanner'
import { OffererSelect } from '@/components/OffererSelect/OffererSelect'

import { CollaboratorsList } from './CollaboratorsList/CollaboratorsList'

// TODO (igabriele, 2026-02-10): Merge that within `<AdministrationLayout />` once `WIP_SWITCH_VENUE` FF is enabled and removed.
const Collaborators = () => {
  const currentOffererId = useAppSelector(
    (state) => state.offerer.currentOfferer
  )?.id
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const selectedVenueAssociated =
    useAppSelector(isSelectedVenueAssociated) ?? true

  const adminSelectedOfferer = useAppSelector(
    (store) => store.user.selectedAdminOfferer
  )
  const offererNames = useAppSelector(ensureOffererNames)
  const offererId = withSwitchVenueFeature
    ? adminSelectedOfferer?.id
    : currentOffererId

  if (!offererId) {
    return null
  }

  return (
    <BasicLayout
      mainHeading="Collaborateurs"
      isAdminArea={withSwitchVenueFeature}
    >
      {withSwitchVenueFeature && offererNames && offererNames.length > 1 && (
        <OffererSelect />
      )}
      {withSwitchVenueFeature && !selectedVenueAssociated && (
        <NonAttachedBanner />
      )}
      {selectedVenueAssociated && <CollaboratorsList />}
    </BasicLayout>
  )
}

// Lazy-loaded by react-router
// ts-unused-exports:disable-next-line
export const Component = Collaborators
