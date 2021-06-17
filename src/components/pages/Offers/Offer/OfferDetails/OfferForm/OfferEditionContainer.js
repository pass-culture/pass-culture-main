import { connect } from 'react-redux'

import OfferEdition from './OfferEdition'

const mapStateToProps = state => ({
  offersSearchFilters: state.offers.searchFilters,
  offersPageNumber: state.offers.pageNumber,
})

export default connect(mapStateToProps)(OfferEdition)
