import cn from 'classnames'
import React from 'react'

import { ILayoutConfig } from 'app/AppRouter/routes_map'

import styles from './AdminLayout.module.scss'
import { Header } from './Header'
import { Menu } from './Menu'

interface IAdminLayoutProps {
  children: React.ReactElement | React.ReactElement[]
  layoutConfig: ILayoutConfig
}

const AdminLayout = ({
  children,
  layoutConfig,
}: IAdminLayoutProps): JSX.Element => {
  const defaultConfig = {
    backTo: null,
    fullscreen: false,
    pageName: 'Accueil',
  }

  const { pageName } = {
    ...defaultConfig,
    ...layoutConfig,
  }
  return (
    <div className={cn(styles['admin-layout'])}>
      <Header />
      <div className={styles['content-wrapper']}>
        <div className={styles['side']}>
          <Menu />
        </div>
        <div className={cn(styles['content'], `${pageName}-page`)}>
          {children}
        </div>
      </div>
    </div>
  )
}
export default AdminLayout
