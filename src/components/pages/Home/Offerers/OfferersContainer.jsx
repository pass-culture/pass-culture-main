import { connect } from 'react-redux'

import { isAPISireneAvailable } from 'store/selectors/data/featuresSelectors'

import Offerers from './Offerers'

export function mapStateToProps(state) {
  return {
    isVenueCreationAvailable: isAPISireneAvailable(state),
  }
}

export default connect(mapStateToProps)(Offerers)
