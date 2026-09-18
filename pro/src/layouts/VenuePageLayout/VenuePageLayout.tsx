import { Outlet, useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { Title } from '@/ui-kit/Title/Title'

import { Header } from '../CollectiveVenuePageLayout/components/Header'

export const VenuePageLayout = () => {
  const location = useLocation()

  const context = location.pathname.includes('page-collective')
    ? 'collective'
    : 'partnerPage'
  const titleText =
    context === 'collective' ? 'Page dans ADAGE' : 'Page sur l’application'

  return (
    <BasicLayout>
      <Title level="1" title={titleText} marginBottom="xxl" />
      <div>
        <Header context={context} />

        <Outlet />
      </div>
    </BasicLayout>
  )
}
