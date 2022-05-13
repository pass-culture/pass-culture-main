import Venues from './Venues'
import { connect } from 'react-redux'
import { isAPISireneAvailable } from 'store/features/selectors'

export const mapStateToProps = state => {
  return {
    isVenueCreationAvailable: isAPISireneAvailable(state),
  }
}

export default connect(mapStateToProps)(Venues)
