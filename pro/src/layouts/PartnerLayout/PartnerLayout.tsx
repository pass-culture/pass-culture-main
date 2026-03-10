import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'

import { getMainHeading } from './utils/getMainHeading'

export const PartnerLayout = () => {
  const currentRoute = useCurrentRoute()
  // TODO (cmoinier): ensureSelectedVenue when WIP_SWITCH_VENUE is activated
  const selectedVenue = useAppSelector((state) => state.user.selectedVenue)

  const mainHeading = getMainHeading(currentRoute, selectedVenue)

  return (
    <BasicLayout mainHeading={mainHeading}>
      <Outlet />
    </BasicLayout>
  )
}
