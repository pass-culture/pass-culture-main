import classnames from 'classnames'
import React from 'react'
import ReactTooltip from 'react-tooltip'

import DomainNameBanner from 'components/DomainNameBanner'
import GoBackLink from 'components/GoBackLink'
import Header from 'components/Header/Header'
import TutorialDialog from 'components/TutorialDialog'

import { ILayoutConfig } from './AppRouter/routes_map'

interface Props {
  children: React.ReactNode
  layoutConfig?: ILayoutConfig
  className?: string
}

const AppLayout = ({ children, layoutConfig, className }: Props) => {
  const defaultConfig: ILayoutConfig = {
    backTo: null,
    fullscreen: false,
    pageName: 'Accueil',
  }

  const { backTo, fullscreen, pageName } = {
    ...defaultConfig,
    ...layoutConfig,
  }

  return (
    <>
      {!fullscreen && <Header />}
      <ReactTooltip
        className="flex-center items-center"
        delayHide={500}
        effect="solid"
        html
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
            <div
              className={classnames('after-notification-content', {
                'with-padding': backTo,
              })}
            >
              <DomainNameBanner />
              {
                /* istanbul ignore next: DEBT, TO FIX */
                backTo && <GoBackLink to={backTo.path} title={backTo.label} />
              }
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
