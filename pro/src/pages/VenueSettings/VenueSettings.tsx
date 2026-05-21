import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { MainHeading } from '@/app/App/layouts/components/MainHeading/MainHeading'
import { SettingsTabs } from '@/components/SettingsTabs/SettingsTabs'

export const VenueSettings = (): JSX.Element => {
  return (
    <BasicLayout>
      <MainHeading mainHeading="Paramètres généraux" />
      <SettingsTabs />
      <Outlet />
    </BasicLayout>
  )
}
