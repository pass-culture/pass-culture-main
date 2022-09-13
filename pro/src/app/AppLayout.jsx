import classnames from 'classnames'
import PropTypes from 'prop-types'
import React from 'react'
import ReactTooltip from 'react-tooltip'

import Header from 'components/layout/Header/Header'
import Notification from 'components/layout/Notification/Notification'
import TutorialDialog from 'components/layout/Tutorial/TutorialDialog'
import DomainNameBanner from 'new_components/DomainNameBanner'
import GoBackLink from 'new_components/GoBackLink'

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
              {backTo && <GoBackLink to={backTo.path} title={backTo.label} />}
              {children}
            </div>
          </div>
        )}
        <TutorialDialog />
        <Notification />
      </main>
    </>
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
