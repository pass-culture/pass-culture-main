import { VenueTypeResponseModel } from 'apiClient/v1'
import { SelectOption } from 'custom_types/form'
import { sortByLabel } from 'utils/strings'

export const buildVenueTypesOptions = (
  venueTypes: VenueTypeResponseModel[]
): SelectOption[] => {
  const wordToNotSort = venueTypes.filter((type) => type.label === 'Autre')
  const sortedTypes = sortByLabel(
    venueTypes.filter((type) => wordToNotSort.indexOf(type) === -1)
  ).concat(wordToNotSort)

  return sortedTypes.map((type) => ({
    value: type.id,
    label: type.label,
  }))
}
