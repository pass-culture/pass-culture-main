import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import { ensureSelectedVenue } from '@/commons/store/user/selectors'

import { getMainHeading } from './utils/getMainHeading'

export const PartnerLayout = () => {
  const currentRoute = useCurrentRoute()
  const selectedVenue = useAppSelector(ensureSelectedVenue)

  const mainHeading = getMainHeading(currentRoute, selectedVenue)

  return (
    <BasicLayout mainHeading={mainHeading}>
      <Outlet />
    </BasicLayout>
  )
}
