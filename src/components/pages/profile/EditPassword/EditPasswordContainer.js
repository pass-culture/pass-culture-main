import { connect } from 'react-redux'
import { requestData } from 'redux-thunk-data'

import { resolveCurrentUser } from '../../../hocs/with-login/withLogin'
import EditPassword from './EditPassword'

const mapDispatchToProps = dispatch => ({
  handleSubmit: (formValues, handleSubmitFail, handleSubmitSuccess) => {
    dispatch(
      requestData({
        apiPath: 'users/current/change-password',
        body: formValues,
        handleFail: handleSubmitFail,
        handleSuccess: handleSubmitSuccess,
        key: 'user',
        method: 'POST',
        resolve: resolveCurrentUser,
      })
    )
  },
})

export default connect(
  null,
  mapDispatchToProps
)(EditPassword)
