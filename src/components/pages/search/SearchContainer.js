import { connect } from 'react-redux'
import { compose } from 'redux'

import Search from './Search'
import { withRequiredLogin } from '../../hocs'
import { resetPageData } from '../../../reducers/data'
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

const mapDispatchToProps = dispatch => ({
  dispatch,
  resetPageData: () => dispatch(resetPageData()),
})

export default compose(
  withRequiredLogin,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Search)
