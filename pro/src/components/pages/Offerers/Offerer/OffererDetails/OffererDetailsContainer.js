/*
* @debt deprecated "Gaël: deprecated usage of redux-saga-data"
* @debt standard "Gaël: prefer hooks for routers (https://reactrouter.com/web/api/Hooks)"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'
import { requestData } from 'redux-saga-data'

import withTracking from 'components/hocs/withTracking'
import { selectOffererById } from 'store/selectors/data/offerersSelectors'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import { selectPhysicalVenuesByOffererId } from 'store/selectors/data/venuesSelectors'
import { offererNormalizer } from 'utils/normalizers'

import OffererDetails from './OffererDetails'
import { makeOffererComponentValueObject } from './OffererFactory'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const {
    params: { offererId },
  } = match
  const currentUser = selectCurrentUser(state)
  return {
    currentUser,
    offerer: makeOffererComponentValueObject(selectOffererById, offererId, state),
    offererId,
    venues: selectPhysicalVenuesByOffererId(state, offererId),
  }
}

/**
 * @debt standard "Annaëlle: Supprimer requestData"
 */
export const mapDispatchToProps = dispatch => {
  return {
    loadOffererById: offererId => {
      dispatch(
        requestData({
          apiPath: `/offerers/${offererId}`,
          normalizer: offererNormalizer,
        })
      )
    },
  }
}

export default compose(
  withRouter,
  withTracking('Offerer'),
  connect(mapStateToProps, mapDispatchToProps)
)(OffererDetails)
