import { connect } from 'react-redux'
import { selectCurrentUser } from '../../../redux/selectors/data/usersSelectors'

import Menu from './Menu'
import { toggleOverlay } from '../../../redux/actions/overlay'

export const mapStateToProps = state => ({
  currentUser: selectCurrentUser(state),
  readRecommendations: state.data.readRecommendations,
})

export const mapDispatchToProps = dispatch => ({
  toggleOverlay: () => dispatch(toggleOverlay()),
})

export default connect(
  mapStateToProps,
  mapDispatchToProps
)(Menu)
