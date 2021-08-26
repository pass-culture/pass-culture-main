/*
* @debt standard "Gaël: prefer hooks for routers (https://reactrouter.com/web/api/Hooks)"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import { showNotification } from 'store/reducers/notificationReducer'

import BookingsRecap from './BookingsRecap'

const mapDispatchToProps = dispatch => ({
  showInformationNotification: () =>
    dispatch(
      showNotification({
        type: 'information',
        text:
          'L’affichage des réservations a été limité à 5 000 réservations. Vous pouvez modifier les filtres pour affiner votre recherche.',
      })
    ),
})

export default compose(withRouter, connect(null, mapDispatchToProps))(BookingsRecap)
