import { connect } from 'react-redux'

import { setUsers } from 'store/reducers/data'
import { showNotificationV2 } from 'store/reducers/notificationReducer'
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
      showNotificationV2({
        type: 'success',
        text: 'Les informations ont bien été enregistrées.',
      })
    ),
})

export default connect(mapStateToProps, mapDispatchToProps)(ProfileAndSupport)
