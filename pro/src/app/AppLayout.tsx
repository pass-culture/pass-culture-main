import classnames from 'classnames'
import React from 'react'

import DomainNameBanner from 'components/DomainNameBanner'
import Header from 'components/Header/Header'
import TutorialDialog from 'components/TutorialDialog'

import { ILayoutConfig } from './AppRouter/routes_map'

export interface AppLayoutProps {
  children?: React.ReactNode
  layoutConfig?: ILayoutConfig
  className?: string
}

const AppLayout = ({ children, layoutConfig, className }: AppLayoutProps) => {
  const defaultConfig: ILayoutConfig = {
    fullscreen: false,
    pageName: 'Accueil',
  }

  const { fullscreen, pageName } = {
    ...defaultConfig,
    ...layoutConfig,
  }

  return (
    <>
      {!fullscreen && <Header />}
      <main
        className={classnames(
          {
            page: true,
            [`${pageName}-page`]: true,
            container: !fullscreen,
            fullscreen,
          },
          className
        )}
      >
        {fullscreen ? (
          children
        ) : (
          <div className="page-content">
            <div className={classnames('after-notification-content')}>
              <DomainNameBanner />
              {children}
            </div>
          </div>
        )}
        <TutorialDialog />
      </main>
    </>
  )
}

export default AppLayout
