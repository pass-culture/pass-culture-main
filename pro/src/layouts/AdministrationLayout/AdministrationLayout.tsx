import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import {
  ensureOffererNames,
  ensureOffererNamesValidated,
} from '@/commons/store/offerer/selectors'
import { NonAttachedBanner } from '@/components/NonAttachedBanner/NonAttachedBanner'
import { OffererSelect } from '@/components/OffererSelect/OffererSelect'

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
  const offererNamesValidated = useAppSelector(ensureOffererNamesValidated)
  const isSelectedOffererValidated = offererNamesValidated.some(
    (offerer) => offerer.id === offererId
  )
  const currentRoute = useCurrentRoute()

  return (
    <BasicLayout mainHeading={currentRoute.handle?.title} isAdminArea>
      {offererNames.length > 1 && <OffererSelect />}
      {isSelectedOffererValidated ? (
        <Outlet />
      ) : (
        <NonAttachedBanner></NonAttachedBanner>
      )}
    </BasicLayout>
  )
}
