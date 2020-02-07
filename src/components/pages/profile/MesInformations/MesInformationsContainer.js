import { connect } from 'react-redux'
import { requestData } from 'redux-thunk-data'
import { resolveCurrentUser } from 'with-react-redux-login'

import MesInformations from './MesInformations'

export const mapStateToProps = (state, ownProps) => {
  return { ...ownProps }
}

export const mapDispatchToProps = dispatch => ({
  handleSubmit: (formValues, handleSubmitFail, handleSubmitSuccess) =>
    dispatch(
      requestData({
        apiPath: 'users/current',
        body: formValues,
        handleFail: handleSubmitFail,
        handleSuccess: handleSubmitSuccess,
        key: 'user',
        method: 'PATCH',
        resolve: resolveCurrentUser,
      })
    ),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(MesInformations)
