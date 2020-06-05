import { connect } from 'react-redux'
import Venues from './Venues'
import selectIsFeatureActive from '../../../../../selectors/data/selectIsFeatureActive'

export const mapStateToProps = state => {
  return {
    isVenueCreationAvailable: selectIsFeatureActive(state, 'API_SIRENE_AVAILABLE'),
  }
}

export default connect(mapStateToProps)(Venues)
