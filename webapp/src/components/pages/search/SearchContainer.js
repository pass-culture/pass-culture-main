import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectUserGeolocation } from '../../../redux/selectors/geolocationSelectors'

import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import { FEATURES } from '../../router/selectors/features'
import selectIsFeatureDisabled from '../../router/selectors/selectIsFeatureDisabled'
import Search from './Search'

export const mapStateToProps = (state, ownProps) => {
  const geolocation = selectUserGeolocation(state)
  const redirectToSearchMainPage = () => {
    const { history } = ownProps
    history.push('/recherche')
  }

  return {
    geolocation,
    redirectToSearchMainPage,
    useAppSearch: !selectIsFeatureDisabled(state, FEATURES.USE_APP_SEARCH_ON_WEBAPP),
  }
}

export default compose(withRequiredLogin, connect(mapStateToProps))(Search)
