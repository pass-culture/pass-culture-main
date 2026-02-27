import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import {
  ensureCurrentOfferer,
  ensureOffererNames,
} from '@/commons/store/offerer/selectors'
import { isSelectedVenueAssociated } from '@/commons/store/user/selectors'
import { NonAttachedBanner } from '@/components/NonAttachedBanner/NonAttachedBanner'
import { OffererSelect } from '@/components/OffererSelect/OffererSelect'
import { ReimbursementsTabs } from '@/components/ReimbursementsTabs/ReimbursementsTabs'

// TODO (igabriele, 2026-02-10): Merge that within `<AdministrationLayout />` once `WIP_SWITCH_VENUE` FF is enabled and removed.
export const Reimbursements = () => {
  const selectedOfferer = useAppSelector(ensureCurrentOfferer)
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const offererNames = useAppSelector(ensureOffererNames)
  const selectedVenueAssociated =
    useAppSelector(isSelectedVenueAssociated) ?? true

  return (
    <BasicLayout
      mainHeading="Gestion financière"
      isAdminArea={withSwitchVenueFeature}
    >
      {withSwitchVenueFeature && offererNames && offererNames.length > 1 && (
        <OffererSelect />
      )}
      {selectedVenueAssociated && (
        <>
          <ReimbursementsTabs selectedOfferer={selectedOfferer} />
          <Outlet />
        </>
      )}
      {withSwitchVenueFeature && !selectedVenueAssociated && (
        <NonAttachedBanner />
      )}
    </BasicLayout>
  )
}
