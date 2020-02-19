import { createSelector } from 'reselect'
import { removeDuplicatesObjects, sortAlphabeticallyArrayOfObjectsByProperty } from '../../utils/array/functions'

export const selectTypes = state => state.data.types

export const selectTypeSublabels = createSelector(
  selectTypes,
  types => {
    const sublabels = types.map(type => type.sublabel)
    return [...new Set(sublabels)].sort()
  }
)

export const selectTypeSublabelsAndDescription = createSelector(
  selectTypes,
  types => {
    const sublabelAndDescription = types.map(type => {
      const { description, sublabel } = type

      return {
        description,
        sublabel
      }
    })
    const uniqueSublabelAndDescription = removeDuplicatesObjects(sublabelAndDescription)
    return uniqueSublabelAndDescription.sort(sortAlphabeticallyArrayOfObjectsByProperty('sublabel'))
  }
)
