import classnames from 'classnames'
import get from 'lodash.get'
import {
  Icon,
  Modal,
  resetForm,
  showNotification,
  Spinner,
  withBlock,
} from 'pass-culture-shared'
import React, { Component, Fragment } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { NavLink } from 'react-router-dom'
import ReactTooltip from 'react-tooltip'
import { compose } from 'redux'

import Header from './Header'
import Notification from './Notification'

class Main extends Component {
  constructor() {
    super()
    this.state = {
      loading: false,
    }
  }

  static defaultProps = {
    Tag: 'main',
  }

  handleDataFail = (state, action) => {
    const { dispatch, payload } = action
    this.setState({ loading: false })

    dispatch(
      showNotification({
        type: 'danger',
        text: get(payload, 'errors.0.global') || 'Erreur de chargement',
      })
    )
  }

  handleDataRequest = () => {
    if (this.props.handleDataRequest) {
      // possibility of the handleDataRequest to return
      // false in order to not trigger the loading
      this.setState({
        loading: true,
      })
      this.props.handleDataRequest(this.handleDataSuccess, this.handleDataFail)
    }
  }

  handleDataSuccess = () => {
    this.setState({
      loading: false,
    })
  }

  componentDidMount() {
    this.props.user && this.handleDataRequest()
  }

  componentDidUpdate(prevProps) {
    const userChanged = !prevProps.user && this.props.user // User just loaded
    const searchChanged =
      this.props.location.search !== prevProps.location.search

    if (userChanged || searchChanged) {
      this.handleDataRequest()
    }
  }

  componentWillUnmount() {
    this.unblock && this.unblock()
    this.props.dispatch(resetForm())
  }

  render() {
    const {
      backTo,
      children,
      fullscreen,
      header,
      name,
      redBg,
      Tag,
      whiteHeader,
      withLoading,
    } = this.props
    const { loading } = this.state
    const footer = [].concat(children).find(e => e && e.type === 'footer')
    const $content = []
      .concat(children)
      .filter(e => e && e.type !== 'header' && e.type !== 'footer')

    return (
      <Fragment>
        {!fullscreen && <Header whiteHeader={whiteHeader} {...header} />}
        <ReactTooltip
          className="flex-center items-center"
          delayHide={500}
          effect="solid"
          html
        />
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
          })}>
          {fullscreen ? (
            <Fragment>
              <Notification isFullscreen />
              {$content}
            </Fragment>
          ) : (
            <div className="columns is-gapless">
              <div className="page-content column is-10 is-offset-1">
                <Notification />
                <div
                  className={classnames('after-notification-content', {
                    'with-padding': backTo,
                  })}>
                  {backTo && (
                    <NavLink
                      to={backTo.path}
                      className="back-button has-text-primary has-text-weight-semibold">
                      <Icon svg="ico-back" />
                      {` ${backTo.label}`}
                    </NavLink>
                  )}
                  <div className="main-content">{$content}</div>
                  {withLoading && loading && <Spinner />}
                </div>
              </div>
            </div>
          )}
          {footer}
        </Tag>
        <Modal key="modal" />
      </Fragment>
    )
  }
}

function mapStateToProps(state) {
  return {
    user: state.user,
  }
}

export default compose(
  withRouter,
  withBlock,
  connect(mapStateToProps)
)(Main)
