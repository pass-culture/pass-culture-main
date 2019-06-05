import { connect } from 'react-redux'

import selectTypeSublabels from '../../../selectors/selectTypes'

import { FilterByOfferTypes } from './FilterByOfferTypes'

const mapStateToProps = state => ({
  typeSublabels: selectTypeSublabels(state),
})

export const FilterByOfferTypesContainer = connect(mapStateToProps)(
  FilterByOfferTypes
)
