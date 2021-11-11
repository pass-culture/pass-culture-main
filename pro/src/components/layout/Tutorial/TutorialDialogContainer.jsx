/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'

import TutorialDialog from 'components/layout/Tutorial/TutorialDialog'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import { setUsers } from '../../../store/reducers/data'

const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
  }
}

const mapDispatchToProps = dispatch => ({
  setUserHasSeenTuto: currentUser => {
    const updatedUser = { ...currentUser, hasSeenProTutorials: true }
    dispatch(setUsers([updatedUser]))
  },
})

export default connect(mapStateToProps, mapDispatchToProps)(TutorialDialog)
