import { connect } from 'react-redux'

import TutorialDialog from 'components/layout/Tutorial/TutorialDialog'
import { setCurrentUser } from 'store/user/actions'
import { selectCurrentUser } from 'store/user/selectors'

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
