import { connect } from 'react-redux'
import { compose } from 'redux'

import { withQueryRouter } from 'components/hocs/with-query-router/withQueryRouter'
import { isAPISireneAvailable } from 'store/features/selectors'

import Offerers from './Offerers'

export const mapStateToProps = state => {
  return {
    isOffererCreationAvailable: isAPISireneAvailable(state),
  }
}

export default compose(withQueryRouter(), connect(mapStateToProps))(Offerers)
