import PropTypes from 'prop-types'
import classnames from 'classnames'
import get from 'lodash.get'
import {
  Modal,
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
    const { user } = this.props
    if (user) this.dataRequestHandler()
  }

  componentDidUpdate(prevProps) {
    const { user, location } = this.props
    const userChanged = !prevProps.user && user // User just loaded
    const searchChanged = location.search !== prevProps.location.search

    if (userChanged || searchChanged) {
      this.dataRequestHandler()
    }
  }

  componentWillUnmount() {
    const { dispatchResetForm } = this.props
    dispatchResetForm()
  }

  handleDataFail = (state, action) => {
    const { dispatchShowNotification } = this.props
    const error = get(action, 'errors.global', []).join('\n')
    dispatchShowNotification({
      text: error || 'Erreur de chargement',
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

    return (
      <React.Fragment>
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
        </Tag>
        <Modal key="modal" />
      </React.Fragment>
    )
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
  children: PropTypes.node.isRequired,
  dispatchResetForm: PropTypes.func.isRequired,
  dispatchShowNotification: PropTypes.func.isRequired,
  footer: PropTypes.object,
  handleDataRequest: PropTypes.func,
  history: PropTypes.object.isRequired,
  location: PropTypes.object.isRequired,
  name: PropTypes.string.isRequired,
  noPadding: PropTypes.bool,
  redBg: PropTypes.bool,
  user: PropTypes.oneOfType([PropTypes.bool, PropTypes.object]),
}

export default compose(
  withRouter,
  withLogin({
    failRedirect: '/connexion',
  }),
  connect(
    state => ({
      notification: state.notification,
      user: state.user,
    }),
    {
      dispatchResetForm: resetForm,
      dispatchShowNotification: showNotification,
    }
  )
)(Main)
