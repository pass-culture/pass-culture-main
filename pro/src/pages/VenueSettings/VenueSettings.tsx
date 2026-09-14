import { Outlet } from 'react-router'

import { BasicLayout } from '@/app/App/layouts/BasicLayout/BasicLayout'
import { SettingsTabs } from '@/components/SettingsTabs/SettingsTabs'

import styles from './VenueSettings.module.scss'

export const VenueSettings = (): JSX.Element => {
  return (
    <BasicLayout>
      <h1 className={styles['title']}>Paramètres</h1>
      <SettingsTabs />
      <Outlet />
    </BasicLayout>
  )
}
