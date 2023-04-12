import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { dehumanizeId } from 'utils/dehumanize'

export const buildOffererOptions = (
  offererNames: TOffererName[]
): {
  offererOptions: SelectOptions
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
  venueList: TOfferIndividualVenue[]
): {
  venueOptions: SelectOptions
  isDisabled: boolean
} => {
  const offererVenues = venueList.filter((venue: TOfferIndividualVenue) => {
    if (!offererId) {
      return false
    }
    const dehumanizedId = dehumanizeId(venue.managingOffererId) || ''
    return dehumanizedId.toString() === offererId
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
