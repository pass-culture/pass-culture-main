import pick from 'lodash.pick'
import uniq from 'lodash.uniq'
import { createSelector } from 'reselect'

import arrayOfObjects, { removeDuplicatesObjects } from '../../utils/arrayOfObjects'

export const selectTypes = state => state.data.types

const selectTypeSublabels = createSelector(
  selectTypes,
  types => {
    const sublabelTypes = uniq(types.map(type => type.sublabel))
    sublabelTypes.sort()
    return sublabelTypes
  }
)

export const selectTypeSublabelsAndDescription = createSelector(
  selectTypes,
  types => {
    const sublabelTypesAndDescription = types.map(type => pick(type, ['description', 'sublabel']))

    const sublabelTypesAndDescriptionFiltred = removeDuplicatesObjects(sublabelTypesAndDescription)

    return sublabelTypesAndDescriptionFiltred.sort(arrayOfObjects('sublabel'))
  }
)

export default selectTypeSublabels
