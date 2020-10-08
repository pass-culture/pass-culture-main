import classnames from 'classnames'
import { Modal } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import ReactTooltip from 'react-tooltip'

import ActionsBar from 'components/layout/ActionsBar'
import HeaderContainer from 'components/layout/Header/HeaderContainer'
import Icon from 'components/layout/Icon'
import NotificationV1Container from 'components/layout/NotificationV1/NotificationV1Container'
import NotificationV2Container from 'components/layout/NotificationV2/NotificationV2Container'

const AppLayout = props => {
  const { PageActionsBar, children, layoutConfig } = props

  const defaultConfig = {
    backTo: null,
    fullscreen: false,
    header: {},
    pageName: 'Acceuil',
    whiteHeader: true,
  }

  const { backTo, fullscreen, header, pageName, whiteHeader } = {
    ...defaultConfig,
    ...layoutConfig,
  }

  return (
    <div>
      {!fullscreen && (
        <HeaderContainer
          whiteHeader={whiteHeader}
          {...header}
        />
      )}

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
          'with-header': Boolean(header),
          'white-header': whiteHeader,
          container: !fullscreen,
          fullscreen,
        })}
      >
        {fullscreen ? (
          <Fragment>
            <NotificationV1Container isFullscreen />
            {children}
          </Fragment>
        ) : (
          <div className="columns is-gapless">
            <div className="page-content column is-10 is-offset-1">
              <NotificationV1Container />
              <div
                className={classnames('after-notification-content', {
                  'with-padding': backTo,
                })}
              >
                {backTo && (
                  <NavLink
                    className="back-button has-text-primary has-text-weight-semibold"
                    to={backTo.path}
                  >
                    <Icon svg="ico-back" />
                    {` ${backTo.label}`}
                  </NavLink>
                )}
                <div className="main-content">
                  {children}
                </div>
              </div>
            </div>
          </div>
        )}
        <NotificationV2Container />
        <Modal key="modal" />
        {PageActionsBar && (
          <ActionsBar>
            <PageActionsBar />
          </ActionsBar>
        )}
      </main>
    </div>
  )
}

AppLayout.defaultProps = {
  layoutConfig: {},
}

AppLayout.propTypes = {
  children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.shape()), PropTypes.shape()])
    .isRequired,
  layoutConfig: PropTypes.shape(),
}

export default AppLayout
