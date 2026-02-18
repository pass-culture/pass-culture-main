import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import { ensureOffererNames } from '@/commons/store/offerer/selectors'
import { OffererSelect } from '@/components/OffererSelect/OffererSelect'

export const AdministrationLayout = () => {
  const offererNames = useAppSelector(ensureOffererNames)
  const currentRoute = useCurrentRoute()

  return (
    <BasicLayout mainHeading={currentRoute.handle?.title} isAdminArea>
      {offererNames.length > 1 && <OffererSelect />}

      <Outlet />
    </BasicLayout>
  )
}
