import { Outlet } from 'react-router'

import { ContentLayout } from '@/app/App/layouts/ContentLayout/ContentLayout'

export const PartnerLayout = () => {
  return (
    <ContentLayout>
      <Outlet />
    </ContentLayout>
  )
}
