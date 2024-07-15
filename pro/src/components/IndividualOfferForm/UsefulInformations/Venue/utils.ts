import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { SelectOption } from 'custom_types/form'
import { computeVenueDisplayName } from 'repository/venuesService'

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
  venueList: VenueListItemResponseModel[]
): {
  venueOptions: SelectOption[]
  isDisabled: boolean
} => {
  const offererVenues = venueList.filter(
    (venue: VenueListItemResponseModel) => {
      if (!offererId) {
        return false
      }
      return venue.managingOffererId.toString() === offererId
    }
  )

  let venueOptions = offererVenues
    .map((venue) => ({
      value: venue.id.toString(),
      label: computeVenueDisplayName(venue),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  if (venueOptions.length !== 1) {
    venueOptions = [
      { value: '', label: 'Sélectionner un lieu' }, // TODO: à supprimer lorsque la feature 'WIP_ENABLE_OFFER_ADDRESS' sera déployée
      ...venueOptions,
    ]
  }

  return {
    venueOptions,
    isDisabled: !offererId || venueOptions.length === 1,
  }
}
