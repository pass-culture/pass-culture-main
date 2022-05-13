import Offerers from './Offerers'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { isAPISireneAvailable } from 'store/features/selectors'

export const mapStateToProps = state => {
  return {
    isOffererCreationAvailable: isAPISireneAvailable(state),
  }
}

export default compose(connect(mapStateToProps))(Offerers)
