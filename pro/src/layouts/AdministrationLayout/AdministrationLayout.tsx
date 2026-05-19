import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { useCurrentUserPermissions } from '@/commons/auth/useCurrentUserPermissions'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import { ensureOffererNames } from '@/commons/store/user/selectors'
import { NonAttachedBanner } from '@/components/NonAttachedBanner/NonAttachedBanner'
import { OffererSelect } from '@/components/OffererSelect/OffererSelect'

export const AdministrationLayout = () => {
  const offererNames = useAppSelector(ensureOffererNames)
  const currentRoute = useCurrentRoute()
  const userPermissions = useCurrentUserPermissions()

  const title = currentRoute.handle?.title

  return (
    <BasicLayout isAdminArea>
      <MainHeading mainHeading={title} />
      {offererNames.length > 1 && <OffererSelect />}
      {userPermissions.isSelectedAdminOffererAssociated ? (
        <Outlet />
      ) : (
        <NonAttachedBanner></NonAttachedBanner>
      )}
    </BasicLayout>
  )
}
