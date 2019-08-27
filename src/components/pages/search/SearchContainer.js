import { connect } from 'react-redux'
import { compose } from 'redux'

import Search from './Search'
import { withRequiredLogin } from '../../hocs'
import selectTypeSublabels, { selectTypes } from './selectors/selectTypes'

const mapStateToProps = state => {
  const { recommendations } = state.data
  const typeSublabels = selectTypeSublabels(state)
  const typeSublabelsAndDescription = selectTypes(state)
  const { user } = state

  return {
    recommendations,
    typeSublabels,
    typeSublabelsAndDescription,
    user,
  }
}

export default compose(
  withRequiredLogin,
  connect(mapStateToProps)
)(Search)
