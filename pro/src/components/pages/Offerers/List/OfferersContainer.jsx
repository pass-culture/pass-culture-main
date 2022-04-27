import { connect } from 'react-redux'
import { compose } from 'redux'

import { isAPISireneAvailable } from 'store/features/selectors'

import Offerers from './Offerers'

export const mapStateToProps = state => {
  return {
    isOffererCreationAvailable: isAPISireneAvailable(state),
  }
}

export default compose(connect(mapStateToProps))(Offerers)
