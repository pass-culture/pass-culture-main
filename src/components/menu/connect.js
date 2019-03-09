import { requestData } from 'redux-saga-data'

import { toggleMainMenu } from '../../reducers/menu'

export const mapStateToProps = state => ({
  readRecommendations: state.data.readRecommendations,
})

export const mapDispatchToProps = dispatch => ({
  onSignoutClick: ({ history, readRecommendations }) => () => {
    function handleRequestSignout() {
      function handleSuccessAfterSignout() {
        history.push('/connexion')
        dispatch(toggleMainMenu())
      }
      dispatch(
        requestData({
          apiPath: '/users/signout',
          handleSuccess: handleSuccessAfterSignout,
        })
      )
    }

    if (!readRecommendations || readRecommendations.length === 0) {
      handleRequestSignout()
      return
    }

    dispatch(
      requestData({
        apiPath: '/recommendations/read',
        body: readRecommendations,
        handleFail: handleRequestSignout,
        handleSuccess: handleRequestSignout,
        method: 'PUT',
      })
    )
  },
})
