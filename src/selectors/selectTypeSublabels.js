import uniq from 'lodash.uniq'
import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.types,
  types => {
    const sublabelTypes = uniq(types.map(type => type.sublabel))
    sublabelTypes.sort()
    return sublabelTypes
  }
)
