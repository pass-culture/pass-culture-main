import get from 'lodash.get'
import PropTypes from 'prop-types'
import React from 'react'

import { showNotification } from 'store/reducers/notificationReducer'

/**
 * @debt standard "Alexis: Deprecated since 04/12/2020. This component should not be used anymore.
 * It has been cleaned from any rendering utility and only stays lifecycle logic for legacy component using it.
 * Should be replaced by an hoc, or component using it should be completely rewritten with hooks."
 */
class Main extends React.PureComponent {
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
      showNotification({
        type: 'error',
        text: get(payload, 'errors.0.global') || 'Erreur de chargement',
      })
    )
  }

  render() {
    return null
  }
}

Main.defaultProps = {
  handleDataRequest: null,
}

Main.propTypes = {
  currentUser: PropTypes.shape().isRequired,
  handleDataRequest: PropTypes.func,
  location: PropTypes.shape().isRequired,
}

export default Main
