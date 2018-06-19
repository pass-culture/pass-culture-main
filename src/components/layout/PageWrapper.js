import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'

import Header from './Header'
import Icon from './Icon'
import { closeNotification } from '../../reducers/notification'

class PageWrapper extends Component {

  handleHistoryBlock = () => {
    const {
      blockers,
      history
    } = this.props
    this.unblock && this.unblock()
    this.unblock = history.block(
      () => {

        // test all the blockers
        for (let blocker of blockers) {
          const {
            block
          } = (blocker || {})
          const shouldBlock = block && block(this.props)
          if (shouldBlock) {
            return false
          }
        }

        // return true by default, which means that we don't block
        // the change of pathname
        return true
      }
    )
  }

  componentDidMount () {
    this.handleHistoryBlock()
  }

  componentDidUpdate (prevProps) {
    if (prevProps.blockers !== this.props.blockers) {
      this.handleHistoryBlock()
    }
  }

  componentWillUnmount() {
      this.unblock && this.unblock()
   }

  render () {
    const {
      backTo,
      closeNotification,
      header,
      Tag,
      name,
      redBg,
      fullscreen,
      children,
      loading,
      notification,
      whiteHeader,
    } = this.props
    const footer = [].concat(children).find(e => e && e.type === 'footer')
    const content = []
      .concat(children)
      .filter(e => e && e.type !== 'header' && e.type !== 'footer')
    return [
      !fullscreen && <Header key='header' whiteHeader={whiteHeader} {...header} />,
      <Tag
        className={classnames({
          page: true,
          [`${name}-page`]: true,
          'with-header': Boolean(header),
          'red-bg': redBg,
          'white-header': whiteHeader,
          container: !fullscreen,
          fullscreen,
          loading,
        })}
        key='page-wrapper'
      >
        { fullscreen ? content : (
          <div className={classnames('page-content')}>
            {notification && (
              <div className={`notification is-${notification.type || 'info'}`}>
                {notification.text}
                <button className="button is-text is-small close" onClick={closeNotification}>
                  OK
                </button>
              </div>
            )}
            <div className='after-notification-content'>
              {backTo && (
                <NavLink to={backTo.path} className='back-button has-text-primary'>
                  <Icon svg='ico-back' />{` ${backTo.label}`}
                </NavLink>
              )}
              {content}
            </div>
          </div>
        )}
        {footer}
      </Tag>
    ]
  }
}

PageWrapper.defaultProps = {
  Tag: 'main',
}

export default compose(
  withRouter,
  connect(
    state => ({
      blockers: state.blockers,
      notification: state.notification
    }),
    { closeNotification }
  )
)(PageWrapper)
