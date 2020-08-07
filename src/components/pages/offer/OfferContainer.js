import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import Offer from './Offer'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'
import { FEATURES } from '../../router/selectors/features'
import { compose } from 'redux'
import { connect } from 'react-redux'

export const mapStateToProps = state => {
  const homepageIsDisabled = selectIsFeatureDisabled(state, FEATURES.HOMEPAGE)

  return {
    homepageIsDisabled,
  }
}

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
  )
)(Offer)
