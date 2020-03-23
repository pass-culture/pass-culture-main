import { connect } from 'react-redux'
import { requestData } from 'redux-thunk-data'
import { resolveCurrentUser, selectCurrentUser } from '../../../hocs/with-login/with-login'
import getDepartementByCode from '../../../../utils/getDepartementByCode'

import MesInformations from './MesInformations'

export const getFormValuesByNames = event => {
  return Array.from(event.target.form)
    .filter(input => !input.disabled)
    .reduce((fields, input) => {
      fields[input.name] = input.value
      return fields
    }, {})
}

export const getDepartment = departmentCode => {
  const departmentName = getDepartementByCode(departmentCode)
  return `${departmentName} (${departmentCode})`
}

export const mapStateToProps = state => ({
  getDepartment,
  getFormValuesByNames,
  user: selectCurrentUser(state),
})

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
