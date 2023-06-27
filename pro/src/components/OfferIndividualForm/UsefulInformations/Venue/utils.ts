import { OffererName } from 'core/Offerers/types'
import { OfferIndividualVenue } from 'core/Venue/types'
import { SelectOption } from 'custom_types/form'

export const buildOffererOptions = (
  offererNames: OffererName[]
): {
  offererOptions: SelectOption[]
  isDisabled: boolean
} => {
  let offererOptions = offererNames
    .map(offerer => ({
      value: offerer.nonHumanizedId.toString(),
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
  venueList: OfferIndividualVenue[]
): {
  venueOptions: SelectOption[]
  isDisabled: boolean
} => {
  const offererVenues = venueList.filter((venue: OfferIndividualVenue) => {
    if (!offererId) {
      return false
    }
    return venue.managingOffererId.toString() === offererId
  })

  let venueOptions = offererVenues
    .map(venue => ({
      value: venue.nonHumanizedId.toString(),
      label: venue.name,
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
