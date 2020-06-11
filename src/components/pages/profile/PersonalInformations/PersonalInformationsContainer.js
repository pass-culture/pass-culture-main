import { connect } from 'react-redux'

import { updateUser } from '../repository/updateUser'
import PersonalInformations from './PersonalInformations'

const mapDispatchToProps = dispatch => ({
  handleSubmit: (formValues, handleSubmitFail, handleSubmitSuccess) => {
    dispatch(updateUser(formValues, handleSubmitFail, handleSubmitSuccess))
  },
})

export default connect(
  null,
  mapDispatchToProps
)(PersonalInformations)
