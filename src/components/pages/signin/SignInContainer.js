import { connect } from 'react-redux'
import { compose } from 'redux'

import { requestData } from '../../../utils/fetch-normalize-data/requestData'
import { FEATURES } from '../../router/selectors/features'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'
import SignIn from './SignIn'

export const mapStateToProps = state => {
  const homepageIsDisabled = selectIsFeatureDisabled(state, FEATURES.HOMEPAGE)

  return {
    homepageIsDisabled,
  }
}

export const mapDispatchToProps = dispatch => ({
  signIn: (values, fail, success) => {
    return new Promise(resolve => {
      dispatch(
        requestData({
          apiPath: '/beneficiaries/signin',
          body: { ...values },
          handleFail: fail(resolve),
          handleSuccess: success(resolve),
          method: 'POST',
        }),
      )
    })
  },
})

export default compose(
  connect(
    mapStateToProps,
    mapDispatchToProps,
  ),
)(SignIn)
