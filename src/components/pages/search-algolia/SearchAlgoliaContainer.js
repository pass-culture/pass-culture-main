import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectUserGeolocation } from '../../../selectors/geolocationSelectors'
import { isGeolocationEnabled, isUserAllowedToSelectCriterion } from '../../../utils/geolocation'

import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import SearchAlgolia from './SearchAlgolia'

export const mapStateToProps = (state, ownProps) => {
  const geolocation = selectUserGeolocation(state)
  const redirectToSearchMainPage = () => {
    const { history } = ownProps
    history.push('/recherche-offres')
  }

  return {
    geolocation,
    isGeolocationEnabled: isGeolocationEnabled(geolocation),
    isUserAllowedToSelectCriterion,
    redirectToSearchMainPage,
  }
}

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(SearchAlgolia)
