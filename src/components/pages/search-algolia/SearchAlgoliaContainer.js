import { compose } from 'redux'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'
import SearchAlgolia from './SearchAlgolia'
import { selectUserGeolocation } from '../../../selectors/geolocationSelectors'

export const mapStateToProps = (state) => {
  const geolocation = selectUserGeolocation(state)

  return {
    geolocation
  }
}
export default compose(withRequiredLogin)(SearchAlgolia)
