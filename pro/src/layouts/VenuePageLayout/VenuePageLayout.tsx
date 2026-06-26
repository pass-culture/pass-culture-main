import { Outlet, useLocation } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'

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
      <MainHeading mainHeading={titleText} />
      <div>
        <Header context={context} />

        <Outlet />
      </div>
    </BasicLayout>
  )
}
