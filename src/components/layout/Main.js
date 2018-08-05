import PropTypes from 'prop-types'
import classnames from 'classnames'
import get from 'lodash.get'
import {
  closeNotification,
  Modal,
  requestData,
  resetForm,
  showNotification,
  withLogin,
} from 'pass-culture-shared'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import BackButton from './BackButton'
import Footer from './Footer'

class Main extends Component {
  static defaultProps = {
    Tag: 'main',
  }

  componentDidMount() {
    this.handleHistoryBlock()
    const { user } = this.props
    if (user) this.dataRequestHandler()
  }

  componentDidUpdate(prevProps) {
    const { blockers, user, location } = this.props
    const blockersChanged = prevProps.blockers !== blockers
    const userChanged = !prevProps.user && user // User just loaded
    const searchChanged = location.search !== prevProps.location.search

    if (blockersChanged) {
      this.handleHistoryBlock()
    }
    if (userChanged || searchChanged) {
      this.dataRequestHandler()
    }
  }

  componentWillUnmount() {
    if (this.unblock) this.unblock()
    const { dispatchResetForm } = this.props
    dispatchResetForm()
  }

  handleDataFail = (state, action) => {
    const { dispatchShowNotification } = this.props
    dispatchShowNotification({
      text:
        get(action, 'errors.global', []).join('\n') || 'Erreur de chargement',
      type: 'danger',
    })
  }

  dataRequestHandler = () => {
    const { handleDataRequest } = this.props
    if (!handleDataRequest) return
    // possibility of the handleDataRequest to return
    // false in order to not trigger the loading
    handleDataRequest(this.handleDataSuccess, this.handleDataFail)
  }

  handleHistoryBlock = () => {
    const { blockers, history } = this.props
    if (this.unblock) this.unblock()
    this.unblock = history.block(() => {
      if (!blockers) {
        return false
      }
      // test all the blockers
      for (const blocker of blockers) {
        const { block } = blocker || {}
        const shouldBlock = block && block(this.props)
        if (shouldBlock) {
          return false
        }
      }
      // return true by default, which means that we don't block
      // the change of pathname
      return true
    })
  }

  render() {
    const {
      backButton,
      children,
      footer: footerProps,
      name,
      noPadding,
      redBg,
      Tag,
    } = this.props
    const header = [].concat(children).find(e => e.type === 'header')
    const footer = [].concat(children).find(e => e.type === 'footer')
    const content = []
      .concat(children)
      .filter(e => e.type !== 'header' && e.type !== 'footer')

    return [
      <Tag
        className={classnames({
          [`${name}-page`]: true,
          'no-padding': noPadding,
          page: true,
          'red-bg': redBg,
          'with-footer': Boolean(footer) || Boolean(footerProps),
          'with-header': Boolean(header),
        })}
        key="main"
      >
        {header}
        {backButton && <BackButton {...backButton} />}
        <div className="page-content">
          {content}
        </div>
        {footer || (footerProps && <Footer {...footerProps} />)}
      </Tag>,
      <Modal key="modal" />,
    ]
  }
}

Main.defaultProps = {
  Tag: 'main',
  backButton: false,
  footer: null,
  handleDataRequest: null,
  noPadding: false,
  redBg: false,
  user: null,
}

Main.propTypes = {
  Tag: PropTypes.string,
  backButton: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
  blockers: PropTypes.array.isRequired,
  children: PropTypes.node.isRequired,
  closeNotification: PropTypes.func.isRequired,
  dispatchResetForm: PropTypes.func.isRequired,
  dispatchShowNotification: PropTypes.func.isRequired,
  footer: PropTypes.object,
  handleDataRequest: PropTypes.func,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  name: PropTypes.string.isRequired,
  noPadding: PropTypes.bool,
  redBg: PropTypes.bool,
  requestData: PropTypes.func.isRequired,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
}

export default compose(
  withRouter,
  withLogin({
    failRedirect: '/connexion',
  }),
  connect(
    state => ({
      blockers: state.blockers,
      notification: state.notification,
      user: state.user,
    }),
    {
      closeNotification,
      dispatchResetForm: resetForm,
      dispatchShowNotification: showNotification,
      requestData,
    }
  )
)(Main)
