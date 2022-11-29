import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import ReactTooltip from 'react-tooltip'

import DomainNameBanner from 'components/DomainNameBanner'
import GoBackLink from 'components/GoBackLink'
import Header from 'components/Header/Header'
import TutorialDialog from 'components/TutorialDialog'
import { USE_ADMIN_LAYOUT } from 'core/shared'

import { AdminLayout } from './AdminLayout'

const AppLayout = props => {
  const { children, layoutConfig } = props

  const defaultConfig = {
    backTo: null,
    fullscreen: false,
    pageName: 'Accueil',
  }

  const { backTo, fullscreen, pageName } = {
    ...defaultConfig,
    ...layoutConfig,
  }

  if (USE_ADMIN_LAYOUT) {
    return <AdminLayout layoutConfig={layoutConfig}>{children}</AdminLayout>
  }

  return (
    <div className="app-layout-root">
      {!fullscreen && <Header />}
      <ReactTooltip
        className="flex-center items-center"
        delayHide={500}
        effect="solid"
        html
      />

      <main
        className={classnames({
          page: true,
          [`${pageName}-page`]: true,
          container: !fullscreen,
          fullscreen,
        })}
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
    </div>
  )
}

AppLayout.defaultProps = {
  layoutConfig: {},
}

AppLayout.propTypes = {
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.shape()),
    PropTypes.shape(),
  ]).isRequired,
  layoutConfig: PropTypes.shape(),
}

export default AppLayout
