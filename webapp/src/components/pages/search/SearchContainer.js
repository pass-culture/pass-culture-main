import { connect } from 'react-redux'
import { compose } from 'redux'
import { selectUserGeolocation } from '../../../redux/selectors/geolocationSelectors'

import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
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
  }
}

export default compose(withRequiredLogin, connect(mapStateToProps))(Search)
