import classnames from 'classnames'
import PropTypes from 'prop-types'
import get from 'lodash.get'
import { closeNotification, Icon } from 'pass-culture-shared'
import React, { Component } from 'react'
import ReactTooltip from 'react-tooltip'

class Notification extends Component {
  dispatchCloseNotification = () => {
    const { dispatch } = this.props
    dispatch(closeNotification())
  }

  componentDidUpdate() {
    const { notification } = this.props
    if (get(notification, 'tooltip')) {
      ReactTooltip.rebuild()
    }
  }

  render() {
    const { isFullscreen, notification } = this.props
    const { text, tooltip, type, url, urlLabel } = notification || {}

    let svg
    if (type === 'success') {
      svg = 'picto-validation'
    } else if (type === 'warning') {
      svg = 'picto-warning'
    } else if (type === 'info') {
      svg = 'picto-info'
    } else if (type === 'tip') {
      svg = 'picto-tip'
    } else {
      svg = 'picto-echec'
    }

    if (!notification) {
      return <div />
    }

    return (
      <div
      className={classnames(`notification is-${type || 'info'}`, {
        fullscreen: isFullscreen
      })}>
        <div
        className={classnames('is-flex fullscreen', {
          'small-padding': !isFullscreen,
        })}>
          <div className="notification-description">
            <Icon svg={svg} />
            <span className="ml8 mb6">{text}</span>
          </div>
          <div className="notification-action-links">
            {url && (
              <a className="close pl12" href={url}>{urlLabel}</a>
            )}
            {tooltip ? (
              <span
              className={classnames({
                'has-text-weight-semibold tooltip small-padding is-2': !isFullscreen,
              })}
              data-place={tooltip.place}
              data-tip={tooltip.tip}
              data-type={tooltip.type}>
              {tooltip.children}
              </span>
            ) : (
              <button
              className="close pl12"
              onClick={this.dispatchCloseNotification}>
              {url ? 'Fermer' : 'OK'}
            </button>
            )}
          </div>
        </div>
      </div>
    )
  }
}

Notification.defaultProps = {
  isFullscreen: false,
  notification: null,
  tooltip: null,
  type: null,
  url: null,
  urlLabel: null
}

Notification.propTypes = {
  dispatch: PropTypes.func.isRequired,
  isFullscreen: PropTypes.bool,
  notification: PropTypes.object,
  text: PropTypes.string,
  tooltip: PropTypes.object,
  type: PropTypes.string,
  url: PropTypes.string,
  urlLabel: PropTypes.string,
}

export default Notification
