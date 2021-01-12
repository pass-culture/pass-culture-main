import { connect } from 'react-redux'

import OfferForm from './OfferForm'

const mapStateToProps = state => ({
  offersSearchFilters: state.offers.searchFilters,
})

export default connect(mapStateToProps)(OfferForm)
