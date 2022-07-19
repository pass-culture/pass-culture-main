import TutorialDialog from 'components/layout/Tutorial/TutorialDialog'
import { connect } from 'react-redux'
import { selectCurrentUser } from 'store/user/selectors'
import { setCurrentUser } from 'store/user/actions'

const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
  }
}

const mapDispatchToProps = dispatch => ({
  setUserHasSeenTuto: currentUser => {
    const updatedUser = { ...currentUser, hasSeenProTutorials: true }
    dispatch(setCurrentUser(updatedUser))
  },
})

export default connect(mapStateToProps, mapDispatchToProps)(TutorialDialog)
