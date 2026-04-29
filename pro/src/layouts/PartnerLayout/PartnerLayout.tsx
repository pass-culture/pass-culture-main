import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'

export const PartnerLayout = () => {
  return (
    <BasicLayout>
      <Outlet />
    </BasicLayout>
  )
}
