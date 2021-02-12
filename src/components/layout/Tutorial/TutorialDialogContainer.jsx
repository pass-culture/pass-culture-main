import { connect } from 'react-redux'

import TutorialDialog from 'components/layout/Tutorial/TutorialDialog'
import { selectIsFeatureActive } from 'store/selectors/data/featuresSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import { setUsers } from '../../../store/reducers/data'

const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
    isFeatureActive: selectIsFeatureActive(state, 'PRO_TUTO'),
  }
}

const mapDispatchToProps = dispatch => ({
  setUserHasSeenTuto: currentUser => {
    const updatedUser = { ...currentUser, hasSeenProTutorials: true }
    dispatch(setUsers([updatedUser]))
  },
})

export default connect(mapStateToProps, mapDispatchToProps)(TutorialDialog)
