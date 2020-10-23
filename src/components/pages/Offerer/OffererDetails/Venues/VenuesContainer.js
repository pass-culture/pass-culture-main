import { connect } from 'react-redux'

import { isAPISireneAvailable } from 'store/selectors/data/featuresSelectors'

import Venues from './Venues'

export const mapStateToProps = state => {
  return {
    isVenueCreationAvailable: isAPISireneAvailable(state),
  }
}

export default connect(mapStateToProps)(Venues)
