import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'

import { getMainHeading } from './utils/getMainHeading'

export const PartnerLayout = () => {
  const currentRoute = useCurrentRoute()
  // TODO (cmoinier): ensureSelectedPartnerVenue once WIP_SWITCH_VENUE is activated
  const selectedPartnerVenue = useAppSelector(
    (state) => state.user.selectedPartnerVenue
  )

  const mainHeading = getMainHeading(currentRoute, selectedPartnerVenue)

  return (
    <BasicLayout mainHeading={mainHeading}>
      <Outlet />
    </BasicLayout>
  )
}
