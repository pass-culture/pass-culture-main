import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { selectIsFeatureActive } from 'store/selectors/data/featuresSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import SignupValidation from './SignupValidation'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
    isNewHomepageActive: selectIsFeatureActive(state, 'PRO_HOMEPAGE'),
  }
}

export default compose(withRouter, connect(mapStateToProps))(SignupValidation)
