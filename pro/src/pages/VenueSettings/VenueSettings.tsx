import { Outlet } from 'react-router'

import { ContentLayout } from '@/app/App/layouts/ContentLayout/ContentLayout'
import { SettingsTabs } from '@/components/SettingsTabs/SettingsTabs'

import styles from './VenueSettings.module.scss'

export const VenueSettings = (): JSX.Element => {
  return (
    <ContentLayout>
      <h1 className={styles['title']}>Paramètres</h1>
      <SettingsTabs />
      <Outlet />
    </ContentLayout>
  )
}
