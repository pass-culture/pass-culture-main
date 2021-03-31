import { connect } from 'react-redux'
import { compose } from 'redux'

import { withQueryRouter } from 'components/hocs/with-query-router/withQueryRouter'
import { saveSearchFilters } from 'store/offers/actions'
import { selectOffers } from 'store/offers/selectors'
import { loadOffers } from 'store/offers/thunks'
import { selectCurrentUser } from 'store/selectors/data/usersSelectors'
import { fetchFromApiWithCredentials } from 'utils/fetch'

import Offers from './Offers'

export const mapStateToProps = state => {
  return {
    currentUser: selectCurrentUser(state),
    getOfferer: fetchOffererById,
    offers: selectOffers(state),
    savedSearchFilters: state.offers.searchFilters,
  }
}

const fetchOffererById = offererId => fetchFromApiWithCredentials(`/offerers/${offererId}`)

export const mapDispatchToProps = dispatch => ({
  loadOffers: filters => dispatch(loadOffers(filters)),
  saveSearchFilters: filters => dispatch(saveSearchFilters(filters)),
})

export default compose(withQueryRouter(), connect(mapStateToProps, mapDispatchToProps))(Offers)
