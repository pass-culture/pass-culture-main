import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import AppLayout from 'app/AppLayout'
import { resetForm } from 'store/reducers/form'
import { showNotificationV1 } from 'store/reducers/notificationReducer'

class Main extends PureComponent {
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

  handleDataSuccess = () => {}

  handleDataRequest = () => {
    const { handleDataRequest } = this.props
    if (handleDataRequest) {
      handleDataRequest(this.handleDataSuccess, this.handleDataFail)
    }
  }

  handleDataFail = (state, action) => {
    const { dispatch, payload } = action
    dispatch(
      showNotificationV1({
        type: 'danger',
        text: get(payload, 'errors.0.global') || 'Erreur de chargement',
      })
    )
  }

  render() {
    const { PageActionsBar, children, layoutConfig } = this.props

    return (
      <AppLayout
        PageActionsBar={PageActionsBar}
        layoutConfig={layoutConfig}
      >
        {children}
      </AppLayout>
    )
  }
}

Main.defaultProps = {
  PageActionsBar: null,
  handleDataRequest: null,
  layoutConfig: {},
}

Main.propTypes = {
  PageActionsBar: PropTypes.elementType,
  children: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  currentUser: PropTypes.shape().isRequired,
  dispatch: PropTypes.func.isRequired,
  handleDataRequest: PropTypes.func,
  layoutConfig: PropTypes.shape(),
  location: PropTypes.shape().isRequired,
}

export default Main
