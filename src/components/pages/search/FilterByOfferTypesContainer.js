import { connect } from 'react-redux'

import { FilterByOfferTypes } from './FilterByOfferTypes'
import selectTypeSublabels from '../../../selectors/selectTypes'

const mapStateToProps = state => ({
  typeSublabels: selectTypeSublabels(state),
})

export const FilterByOfferTypesContainer = connect(mapStateToProps)(
  FilterByOfferTypes
)
