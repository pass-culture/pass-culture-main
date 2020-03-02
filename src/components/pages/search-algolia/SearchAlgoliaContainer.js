import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectUserGeolocation } from '../../../selectors/geolocationSelectors'

import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import SearchAlgolia from './SearchAlgolia'

export const mapStateToProps = (state, ownProps) => {
  const geolocation = selectUserGeolocation(state)
  const isGeolocationEnabled = () => {
    const { latitude, longitude } = geolocation
    return longitude && latitude ? true : false
  }
  const redirectToSearchMainPage = () => {
    const { history } = ownProps
    history.push('/recherche-offres')
  }
  return {
    geolocation,
    redirectToSearchMainPage,
    isGeolocationEnabled,
  }
}

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(SearchAlgolia)
