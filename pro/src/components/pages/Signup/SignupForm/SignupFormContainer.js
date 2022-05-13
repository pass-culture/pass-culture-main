import * as pcapi from 'repository/pcapi/pcapi'

import SignupForm from './SignupForm'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { removeErrors } from 'store/reducers/errors'
import { removeWhitespaces } from 'react-final-form-utils'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import { showNotification } from 'store/reducers/notificationReducer'
import { withRouter } from 'utils/withRouter'

const STATE_ERROR_NAME = 'user'

export const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
})

export const mapDispatchToProps = (dispatch, ownProps) => ({
  createNewProUser: (payload, onHandleFail, onHandleSuccess) => {
    dispatch(removeErrors(STATE_ERROR_NAME))

    const { firstName, siren } = payload
    pcapi
      .signup({
        ...payload,
        siren: removeWhitespaces(siren),
        publicName: firstName,
      })
      .then(() => onHandleSuccess())
      .catch(response => onHandleFail(response.errors ? response.errors : {}))
  },

  redirectToConfirmation: () => {
    ownProps.history.replace('/inscription/confirmation')
  },

  notifyError: message => {
    dispatch(
      showNotification({
        text: message,
        type: 'error',
      })
    )
  },
})

export default compose(
  withRouter,
  connect(mapStateToProps, mapDispatchToProps)
)(SignupForm)
