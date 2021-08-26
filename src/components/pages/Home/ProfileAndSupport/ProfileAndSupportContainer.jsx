/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'

import { setUsers } from 'store/reducers/data'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import ProfileAndSupport from './ProfileAndSupport'

export function mapStateToProps(state) {
  return {
    user: selectCurrentUser(state),
  }
}

const mapDispatchToProps = dispatch => ({
  setUserInformations: (user, updatedInformations) => {
    const updatedUser = { ...user, ...updatedInformations }
    dispatch(setUsers([updatedUser]))
  },
  showSuccessNotification: () =>
    dispatch(
      showNotification({
        type: 'success',
        text: 'Les informations ont bien été enregistrées.',
      })
    ),
})

export default connect(mapStateToProps, mapDispatchToProps)(ProfileAndSupport)
