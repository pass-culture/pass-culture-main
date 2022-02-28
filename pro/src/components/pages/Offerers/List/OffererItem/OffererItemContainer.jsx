import { connect } from 'react-redux'

import { isAPISireneAvailable } from 'store/features/selectors'

import OffererItem from './OffererItem'

export const mapStateToProps = state => {
  return {
    isVenueCreationAvailable: isAPISireneAvailable(state),
  }
}

export default connect(mapStateToProps)(OffererItem)
