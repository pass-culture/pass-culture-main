import classnames from 'classnames'
import get from 'lodash.get'
import {
  Icon,
  Modal,
  resetForm,
  showNotification,
  Spinner,
} from 'pass-culture-shared'
import React, { Component, Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import ReactTooltip from 'react-tooltip'

import HeaderContainer from 'components/layout/Header/HeaderContainer'
import NotificationContainer from "../Notification/NotificationContainer";

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
    const { currentUser } = this.props
    if (currentUser) {
      this.handleDataRequest()
    }
  }

  componentDidUpdate(prevProps) {
    const { currentUser, location } = this.props
    const { search } = location
    const userChanged = !prevProps.currentUser && currentUser // User just loaded
    const searchChanged = search !== prevProps.location.search

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
        {!fullscreen && (
          <HeaderContainer whiteHeader={whiteHeader} {...header} />
        )}
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
              <NotificationContainer isFullscreen />
              {$content}
            </Fragment>
          ) : (
            <div className="columns is-gapless">
              <div className="page-content column is-10 is-offset-1">
                <NotificationContainer />
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

export default Main
