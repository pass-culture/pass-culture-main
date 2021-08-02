import { connect } from 'react-redux'
import { compose } from 'redux'

import { withQueryRouter } from 'components/hocs/with-query-router/withQueryRouter'
import * as pcapi from 'repository/pcapi/pcapi'
import { showNotification } from 'store/reducers/notificationReducer'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'

import Offers from './Offers'

export const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
    getOfferer: pcapi.getOfferer,
  }
}

export const mapDispatchToProps = dispatch => ({
  showInformationNotification: information =>
    dispatch(
      showNotification({
        type: 'information',
        text: information,
      })
    ),
})

export default compose(withQueryRouter(), connect(mapStateToProps, mapDispatchToProps))(Offers)
