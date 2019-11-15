import { connect } from 'react-redux'

import FilterByOfferTypes from './FilterByOfferTypes'
import { selectTypeSublabels } from '../../../../selectors/data/typesSelectors'

const mapStateToProps = state => ({
  typeSublabels: selectTypeSublabels(state),
})

export default connect(mapStateToProps)(FilterByOfferTypes)
