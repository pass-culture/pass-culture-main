import uniq from 'lodash.uniq'
import { createSelector } from 'reselect'

const selectTypeSublabels = createSelector(
  state => state.data.types,
  types => {
    const sublabelTypes = uniq(types.map(type => type.sublabel))
    sublabelTypes.sort()
    return sublabelTypes
  }
)

export const selectTypes = createSelector(
  state => state.data.types,
  types => {
    const sublabelTypes = uniq(types)
    sublabelTypes.sort()
    return sublabelTypes
  }
)

export default selectTypeSublabels
