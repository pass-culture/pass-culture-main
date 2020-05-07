import { connect } from 'react-redux'
import { requestData } from 'redux-thunk-data'

import { resolveCurrentUser } from '../../../../redux/selectors/data/usersSelectors'
import PersonalInformations from './PersonalInformations'

const mapDispatchToProps = dispatch => ({
  handleSubmit: (formValues, handleSubmitFail, handleSubmitSuccess) => {
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
    )
  },
})

export default connect(
  null,
  mapDispatchToProps
)(PersonalInformations)
