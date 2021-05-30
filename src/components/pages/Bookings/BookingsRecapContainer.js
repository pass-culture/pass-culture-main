import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { isFeatureActive } from 'store/features/selectors'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectIsUserAdmin } from 'store/selectors/data/usersSelectors'

import BookingsRecap from './BookingsRecap'

export function mapStateToProps(state) {
  return {
    isUserAdmin: selectIsUserAdmin(state),
    arePreFiltersEnabled: isFeatureActive(state, 'ENABLE_BOOKINGS_PAGE_FILTERS_FIRST'),
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
