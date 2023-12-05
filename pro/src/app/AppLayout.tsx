import classnames from 'classnames'
import React from 'react'

import DomainNameBanner from 'components/DomainNameBanner'
import Header from 'components/Header/Header'
import SkipLinks from 'components/SkipLinks'

export interface AppLayoutProps {
  children?: React.ReactNode
  pageName?: string
  fullscreen?: boolean
  className?: string
}

export const AppLayout = ({
  children,
  className,
  pageName = 'Accueil',
  fullscreen = false,
}: AppLayoutProps) => (
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
