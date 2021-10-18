/*
* @debt complexity "Gaël: file nested too deep in directory structure"
* @debt standard "Gaël: prefer useSelector hook vs connect for redux (https://react-redux.js.org/api/hooks)"
*/

import { connect } from 'react-redux'

import OfferEdition from './OfferEdition'

const mapStateToProps = state => ({
  offersSearchFilters: state.offers.searchFilters,
  offersPageNumber: state.offers.pageNumber,
})

export default connect(mapStateToProps)(OfferEdition)
