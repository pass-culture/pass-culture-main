import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureOffererNames } from '@/commons/store/offerer/selectors'
import { OffererSelect } from '@/components/OffererSelect/OffererSelect'
import { ReimbursementsTabs } from '@/components/ReimbursementsTabs/ReimbursementsTabs'

// TODO (igabriele, 2026-02-10): Merge that within `<AdministrationLayout />` once `WIP_SWITCH_VENUE` FF is enabled and removed.
export const Reimbursements = () => {
  const currentOfferer = useAppSelector((state) => state.offerer.currentOfferer)
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const offererNames = useAppSelector(ensureOffererNames)

  const adminSelectedOfferer = useAppSelector(
    (store) => store.user.selectedAdminOfferer
  )

  const selectedOfferer = withSwitchVenueFeature
    ? adminSelectedOfferer
    : currentOfferer
  assertOrFrontendError(selectedOfferer, '`selectedOfferer` is undefined')

  return (
    <BasicLayout
      mainHeading="Gestion financière"
      isAdminArea={withSwitchVenueFeature}
    >
      {withSwitchVenueFeature && offererNames && offererNames.length > 1 && (
        <OffererSelect />
      )}
      <ReimbursementsTabs selectedOfferer={selectedOfferer} />
      <Outlet />
    </BasicLayout>
  )
}
