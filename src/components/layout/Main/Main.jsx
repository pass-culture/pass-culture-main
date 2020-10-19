import classnames from 'classnames'
import get from 'lodash.get'
import { Icon, Modal, resetForm, Spinner } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { PureComponent, Fragment } from 'react'
import { NavLink } from 'react-router-dom'
import ReactTooltip from 'react-tooltip'

import ActionsBar from '../ActionsBar/'
import HeaderContainer from 'components/layout/Header/HeaderContainer'
import NotificationV1Container from 'components/layout/NotificationV1/NotificationV1Container'
import { showNotificationV1 } from 'store/reducers/notificationReducer'

class Main extends PureComponent {
  constructor() {
    super()
    this.state = {
      loading: false,
    }
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
    const { dispatch } = this.props
    dispatch(resetForm())
  }

  handleDataSuccess = () => {
    this.setState({
      loading: false,
    })
  }

  handleDataRequest = () => {
    const { handleDataRequest } = this.props
    if (handleDataRequest) {
      // possibility of the handleDataRequest to return
      // false in order to not trigger the loading
      this.setState({
        loading: true,
      })
      handleDataRequest(this.handleDataSuccess, this.handleDataFail)
    }
  }

  handleDataFail = (state, action) => {
    const { dispatch, payload } = action
    this.setState({ loading: false })

    dispatch(
      showNotificationV1({
        type: 'danger',
        text: get(payload, 'errors.0.global') || 'Erreur de chargement',
      })
    )
  }

  render() {
    const {
      PageActionsBar,
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
        >
          {fullscreen ? (
            <Fragment>
              <NotificationV1Container isFullscreen />
              {$content}
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
                    {$content}
                  </div>
                  {withLoading && loading && <Spinner />}
                </div>
              </div>
            </div>
          )}
          {footer}
        </Tag>
        <Modal key="modal" />
        { PageActionsBar && <ActionsBar><PageActionsBar/></ActionsBar>}

      </Fragment>
    )
  }
}

Main.defaultProps = {
  Tag: 'main',
  PageActionsBar: null,
  backTo: null,
  fullscreen: false,
  handleDataRequest: null,
  header: {},
  redBg: null,
  whiteHeader: null,
  withLoading: null,
}

Main.propTypes = {
  Tag: PropTypes.string,
  PageActionsBar: PropTypes.elementType,
  backTo: PropTypes.shape(),
  children: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  currentUser: PropTypes.shape().isRequired,
  dispatch: PropTypes.func.isRequired,
  fullscreen: PropTypes.bool,
  handleDataRequest: PropTypes.func,
  header: PropTypes.shape(),
  location: PropTypes.shape().isRequired,
  name: PropTypes.string.isRequired,
  redBg: PropTypes.string,
  whiteHeader: PropTypes.string,
  withLoading: PropTypes.bool,
}

export default Main
