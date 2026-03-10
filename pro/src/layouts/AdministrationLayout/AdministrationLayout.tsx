import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import {
  ensureOffererNames,
  ensureOffererNamesAttached,
} from '@/commons/store/offerer/selectors'
import { OffererSelect } from '@/components/OffererSelect/OffererSelect'
import { NonAttachedBanner } from '@/pages/NonAttached/NonAttachedBanner/NonAttachedBanner'

export const AdministrationLayout = () => {
  const withSwitchVenueFeature = useActiveFeature('WIP_SWITCH_VENUE')
  const offererNames = useAppSelector(ensureOffererNames)
  const currentOffererId = useAppSelector(
    (state) => state.offerer.currentOfferer
  )?.id
  const adminSelectedOfferer = useAppSelector(
    (store) => store.user.selectedAdminOfferer
  )
  const offererId = withSwitchVenueFeature
    ? adminSelectedOfferer?.id
    : currentOffererId
  const offererNamesAttached = useAppSelector(ensureOffererNamesAttached)
  const isSelectedOffererAttached = offererNamesAttached.some(
    (offerer) => offerer.id === offererId
  )
  const currentRoute = useCurrentRoute()

  return (
    <BasicLayout mainHeading={currentRoute.handle?.title} isAdminArea>
      {offererNames.length > 1 && <OffererSelect />}
      {isSelectedOffererAttached ? (
        <Outlet />
      ) : (
        <NonAttachedBanner></NonAttachedBanner>
      )}
    </BasicLayout>
  )
}
