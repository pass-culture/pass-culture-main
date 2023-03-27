import classnames from 'classnames'
import React from 'react'
import ReactTooltip from 'react-tooltip'

import DomainNameBanner from 'components/DomainNameBanner'
import Header from 'components/Header/Header'
import SkipLinks from 'components/SkipLinks'
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
      {!fullscreen && (
        <>
          <SkipLinks />
          <Header />
        </>
      )}
      <ReactTooltip
        className="flex-center items-center"
        delayHide={500}
        effect="solid"
        html
      />

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
        <TutorialDialog />
      </main>
    </>
  )
}

export default AppLayout
