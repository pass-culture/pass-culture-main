import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { SettingsTabs } from '@/components/SettingsTabs/SettingsTabs'
import { Title } from '@/ui-kit/Title/Title'

export const VenueSettings = (): JSX.Element => {
  return (
    <BasicLayout>
      <Title level="1" title="Paramètres" marginBottom="xxl" />
      <SettingsTabs />
      <Outlet />
    </BasicLayout>
  )
}
