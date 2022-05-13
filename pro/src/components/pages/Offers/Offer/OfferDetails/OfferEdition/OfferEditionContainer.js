import OfferEdition from './OfferEdition'
import { connect } from 'react-redux'

const mapStateToProps = state => ({
  offersSearchFilters: state.offers.searchFilters,
  offersPageNumber: state.offers.pageNumber,
})

export default connect(mapStateToProps)(OfferEdition)
