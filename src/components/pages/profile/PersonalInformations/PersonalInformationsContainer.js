import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'
import { withRouter } from 'react-router-dom'
import { toast } from 'react-toastify'

import {
  selectCurrentUser,
  resolveCurrentUser,
} from '../../../../redux/selectors/data/usersSelectors'
import getDepartementByCode from '../../../../utils/getDepartementByCode'
import PersonalInformations from './PersonalInformations'

export const getDepartment = departmentCode => {
  const departmentName = getDepartementByCode(departmentCode)
  return `${departmentName} (${departmentCode})`
}

export const mapStateToProps = state => ({
  getDepartment,
  toast,
  pathToProfile: '/profil',
  user: selectCurrentUser(state),
})

export const mapDispatchToProps = dispatch => ({
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

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(PersonalInformations)
