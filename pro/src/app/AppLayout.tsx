import classnames from 'classnames'
import React from 'react'

import DomainNameBanner from 'components/DomainNameBanner'
import Header from 'components/Header/Header'
import SkipLinks from 'components/SkipLinks'

export interface AppLayoutProps {
  children?: React.ReactNode
  pageName?: string
  className?: string
  layout?: 'basic' | 'funnel' | 'without-nav'
}

export const AppLayout = ({
  children,
  className,
  pageName = 'Accueil',
  layout = 'basic',
}: AppLayoutProps) => (
  <>
    <SkipLinks />
    {layout == 'basic' && <Header />}
    <main
      id="content"
      className={classnames(
        {
          page: true,
          [`${pageName}-page`]: true,
          container: layout === 'basic',
          'without-nav': layout === 'without-nav',
        },
        className
      )}
    >
      {layout === 'funnel' || layout === 'without-nav' ? (
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
