import classnames from 'classnames'
import React from 'react'
import { Tooltip } from 'react-tooltip'

import DomainNameBanner from 'components/DomainNameBanner'
import Header from 'components/Header/Header'
import TutorialDialog from 'components/TutorialDialog'

import { ILayoutConfig } from './AppRouter/routes_map'
import 'react-tooltip/dist/react-tooltip.css'

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
      <Tooltip
        className="type-info flex-center items-center"
        delayHide={500}
        anchorSelect=".react-tooltip-anchor"
      />

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
