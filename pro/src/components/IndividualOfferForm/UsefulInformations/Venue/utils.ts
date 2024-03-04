import { GetOffererNameResponseModel } from 'apiClient/v1'
import { IndividualOfferVenueItem } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'

export const buildOffererOptions = (
  offererNames: GetOffererNameResponseModel[]
): {
  offererOptions: SelectOption[]
  isDisabled: boolean
} => {
  let offererOptions = offererNames
    .map((offerer) => ({
      value: offerer.id.toString(),
      label: offerer.name,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  if (offererOptions.length !== 1) {
    offererOptions = [
      { value: '', label: 'Selectionner une structure' },
      ...offererOptions,
    ]
  }

  return {
    offererOptions,
    isDisabled: offererOptions.length === 1,
  }
}

export const buildVenueOptions = (
  offererId: string,
  venueList: IndividualOfferVenueItem[]
): {
  venueOptions: SelectOption[]
  isDisabled: boolean
} => {
  const offererVenues = venueList.filter((venue: IndividualOfferVenueItem) => {
    if (!offererId) {
      return false
    }
    return venue.managingOffererId.toString() === offererId
  })

  let venueOptions = offererVenues
    .map((venue) => ({
      value: venue.id.toString(),
      label: venue.publicName || venue.name,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  if (venueOptions.length !== 1) {
    venueOptions = [
      { value: '', label: 'Sélectionner un lieu' },
      ...venueOptions,
    ]
  }

  return {
    venueOptions,
    isDisabled: !offererId || venueOptions.length === 1,
  }
}
