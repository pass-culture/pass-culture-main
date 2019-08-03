import pick from 'lodash.pick'
import uniq from 'lodash.uniq'
import { createSelector } from 'reselect'

import arrayOfObjects, { removeDuplicatesObjects } from '../../../../utils/arrayOfObjects'

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
    const sublabelTypesAndDescription = types.map(type => pick(type, ['description', 'sublabel']))

    const sublabelTypesAndDescriptionFiltred = removeDuplicatesObjects(sublabelTypesAndDescription)

    return sublabelTypesAndDescriptionFiltred.sort(arrayOfObjects('sublabel'))
  }
)

export default selectTypeSublabels
