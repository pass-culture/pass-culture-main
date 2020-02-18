import { compose } from 'redux'
import { connect } from 'react-redux'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import SearchAlgolia from './SearchAlgolia'
import { selectUserGeolocation } from '../../../selectors/geolocationSelectors'

export const mapStateToProps = (state, ownProps) => {
  const geolocation = selectUserGeolocation(state)
  const redirectToSearchMainPage = () => {
    const { history } = ownProps
    history.push('/recherche-offres')
  }
  return {
    geolocation,
    redirectToSearchMainPage,
  }
}

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(SearchAlgolia)
