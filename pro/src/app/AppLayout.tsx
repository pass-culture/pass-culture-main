import classnames from 'classnames'
import React from 'react'

import DomainNameBanner from 'components/DomainNameBanner'
import Header from 'components/Header/Header'
import SkipLinks from 'components/SkipLinks'

import { ILayoutConfig } from './AppRouter/routesMap'

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
      {!fullscreen && (
        <>
          <SkipLinks />
          <Header />
        </>
      )}

      <main
        id="content"
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
      </main>
    </>
  )
}

export default AppLayout
