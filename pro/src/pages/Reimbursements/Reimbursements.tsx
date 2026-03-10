import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import {
  ensureCurrentOfferer,
  ensureOffererNames,
  ensureOffererNamesAttached,
} from '@/commons/store/offerer/selectors'
import { OffererSelect } from '@/components/OffererSelect/OffererSelect'
import { ReimbursementsTabs } from '@/components/ReimbursementsTabs/ReimbursementsTabs'

import { NonAttachedBanner } from '../NonAttached/NonAttachedBanner/NonAttachedBanner'

// TODO (igabriele, 2026-02-10): Merge that within `<AdministrationLayout />` once `WIP_SWITCH_VENUE` FF is enabled and removed.
export const Reimbursements = () => {
  const selectedOfferer = useAppSelector(ensureCurrentOfferer)
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const offererNames = useAppSelector(ensureOffererNames)
  const adminSelectedOfferer = useAppSelector(
    (store) => store.user.selectedAdminOfferer
  )
  const offererId = withSwitchVenueFeature
    ? adminSelectedOfferer?.id
    : selectedOfferer?.id
  const offererNamesAttached = useAppSelector(ensureOffererNamesAttached)
  const isSelectedOffererAttached = offererNamesAttached.some(
    (offerer) => offerer.id === offererId
  )
  return (
    <BasicLayout
      mainHeading="Gestion financière"
      isAdminArea={withSwitchVenueFeature}
    >
      {withSwitchVenueFeature && offererNames && offererNames.length > 1 && (
        <OffererSelect />
      )}
      {isSelectedOffererAttached ? (
        <>
          <ReimbursementsTabs selectedOfferer={selectedOfferer} />
          <Outlet />
        </>
      ) : (
        <NonAttachedBanner></NonAttachedBanner>
      )}
    </BasicLayout>
  )
}
