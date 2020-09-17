import PropTypes from 'prop-types'
import React, { useEffect, useState } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import { fetchCurrentUser } from '../../../redux/actions/currentUser'
import LoadingPage from '../../layout/LoadingPage/LoadingPage'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'
import { FEATURES } from '../../router/selectors/features'

export default ({
  isRequired,
  handleSuccess = () => null,
  handleFail = () => null,
}) => WrappedComponent => {
  const _withLogin = props => {
    const { dispatchFetchCurrentUser, history, isHomepageDisabled, location } = props
    const [loading, setLoading] = useState(true)

    useEffect(() => {
      dispatchFetchCurrentUser().then(({ value: currentUser }) => {
        const isLoggedIn = !!currentUser

        if (isLoggedIn) handleSuccess({ currentUser, history, isHomepageDisabled, location })
        else handleFail(history, location)

        if (!isRequired || isLoggedIn) setLoading(false)
      })
    }, [])

    return loading ? <LoadingPage /> : <WrappedComponent {...props} />
  }

  _withLogin.defaultProps = {
    isHomepageDisabled: true,
  }

  _withLogin.propTypes = {
    dispatchFetchCurrentUser: PropTypes.func.isRequired,
    history: PropTypes.shape({
      push: PropTypes.func.isRequired,
    }).isRequired,
    isHomepageDisabled: PropTypes.bool,
    location: PropTypes.shape({
      pathname: PropTypes.string.isRequired,
      search: PropTypes.string.isRequired,
    }).isRequired,
  }

  const mapStateToProps = state => {
    return {
      isHomepageDisabled: selectIsFeatureDisabled(state, FEATURES.HOMEPAGE),
    }
  }

  return compose(
    withRouter,
    connect(
      mapStateToProps,
      { dispatchFetchCurrentUser: fetchCurrentUser },
    ),
  )(_withLogin)
}
