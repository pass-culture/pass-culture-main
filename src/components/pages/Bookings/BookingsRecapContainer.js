import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import BookingsRecap from './BookingsRecap'

export function mapStateToProps(state) {
  return {
    currentUser: selectCurrentUser(state),
  }
}

const mapDispatchToProps = dispatch => ({
  showWarningNotification: () =>
    dispatch(
      showNotification({
        type: 'warning',
        text:
          'Vous avez été limité à 5 000 réservations. Veuillez contacter le support si nécessaire.',
      })
    ),
})

export default compose(withRouter, connect(mapStateToProps, mapDispatchToProps))(BookingsRecap)
