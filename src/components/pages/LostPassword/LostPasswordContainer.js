import { searchSelector } from 'pass-culture-shared'
import { connect } from 'react-redux'
import LostPassword from './LostPassword'

export const mapStateToProps = (state, ownProps) => {
  const userErrors = state.errors.user || []
  const {
    location: { search },
  } = ownProps
  const { change, envoye, token } = searchSelector(state, search)
  return {
    change,
    errors: userErrors,
    envoye,
    token,
  }
}

export default connect(mapStateToProps)(LostPassword)
