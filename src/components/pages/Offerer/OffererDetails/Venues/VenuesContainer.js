import { connect } from 'react-redux'
import Venues from './Venues'
import { isAPISireneAvailable } from '../../../../../selectors/data/featuresSelectors'

export const mapStateToProps = state => {
  return {
    isVenueCreationAvailable: isAPISireneAvailable(state),
  }
}

export default connect(mapStateToProps)(Venues)
