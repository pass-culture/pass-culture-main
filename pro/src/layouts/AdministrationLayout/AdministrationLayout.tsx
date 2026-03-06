import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import { ensureOffererNames } from '@/commons/store/offerer/selectors'
import { isSelectedVenueAssociated } from '@/commons/store/user/selectors'
import { NonAttachedBanner } from '@/components/NonAttachedBanner/NonAttachedBanner'
import { OffererSelect } from '@/components/OffererSelect/OffererSelect'

export const AdministrationLayout = () => {
  const offererNames = useAppSelector(ensureOffererNames)
  const currentRoute = useCurrentRoute()
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const selectedVenueAssociated =
    useAppSelector(isSelectedVenueAssociated) ?? true

  return (
    <BasicLayout mainHeading={currentRoute.handle?.title} isAdminArea>
      {offererNames.length > 1 && <OffererSelect />}
      {withSwitchVenueFeature && !selectedVenueAssociated && (
        <NonAttachedBanner />
      )}
      {selectedVenueAssociated && <Outlet />}
    </BasicLayout>
  )
}
