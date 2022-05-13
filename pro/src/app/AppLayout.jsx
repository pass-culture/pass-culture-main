import DomainNameBanner from 'new_components/DomainNameBanner'
import HeaderContainer from 'components/layout/Header/HeaderContainer'
import Icon from 'components/layout/Icon'
import { NavLink } from 'react-router-dom'
import NotificationContainer from 'components/layout/Notification/NotificationContainer'
import PropTypes from 'prop-types'
import React from 'react'
import ReactTooltip from 'react-tooltip'
import TutorialDialogContainer from 'components/layout/Tutorial/TutorialDialogContainer'
import classnames from 'classnames'

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
      {!fullscreen && <HeaderContainer />}
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
              {backTo && (
                <NavLink
                  className="back-button has-text-primary"
                  to={backTo.path}
                >
                  <Icon svg="ico-back" />
                  {` ${backTo.label}`}
                </NavLink>
              )}
              {children}
            </div>
          </div>
        )}
        <TutorialDialogContainer />
        <NotificationContainer />
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
