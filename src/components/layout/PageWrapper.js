import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import { compose } from 'redux'
import get from 'lodash.get'

import withLogin from '../hocs/withLogin'
import Header from './Header'
import Icon from './Icon'
import Loader from './Loader'
import { showNotification, closeNotification } from '../../reducers/notification'
import { requestData } from '../../reducers/data'

class PageWrapper extends Component {

  constructor () {
    super()
    this.state = {
      loading: false,
    }
  }

  static defaultProps = {
    Tag: 'main',
  }


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

  handleDataRequest = () => {
    if (this.props.handleDataRequest) {
      // possibility of the handleDataRequest to return
      // false in orde to not trigger the loading
      const loading = this.props.handleDataRequest(
        this.handleDataSuccess,
        this.handleDataFail
      ) === false ? false : true
      this.setState({
        loading
      })
    }
  }

  handleDataSuccess = (state, action) => {
    this.setState({
      loading: false,
    })
  }

  handleDataFail = (state, action) => {
    this.setState({
      loading: false,
    })
    this.props.showNotification({
      type: 'danger',
      text: get(action, 'errors.global', []).join('\n') || 'Erreur de chargement'
    })
  }

  componentDidMount () {
    this.handleHistoryBlock()
    this.props.user && this.handleDataRequest()
  }

  componentDidUpdate (prevProps) {
    if (prevProps.blockers !== this.props.blockers) {
      this.handleHistoryBlock()
    }
    if (!prevProps.user && this.props.user) { // User just loaded
      this.handleDataRequest()
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
      notification,
      whiteHeader,
    } = this.props
    const {
      loading
    } = this.state
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
              <div className='pc-content'>
                {content}
              </div>
              {loading && <Loader />}
            </div>
          </div>
        )}
        {footer}
      </Tag>
    ]
  }
}

export default compose(
  withRouter,
  withLogin(),
  connect(
    state => ({
      blockers: state.blockers,
      notification: state.notification,
      user: state.user,
    }),
    {
      showNotification,
      closeNotification,
      requestData,
    }
  )
)(PageWrapper)
