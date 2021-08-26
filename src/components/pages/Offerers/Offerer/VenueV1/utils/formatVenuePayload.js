/*
* @debt complexity "Gaël: the file contains eslint error(s) based on our new config"
* @debt complexity "Gaël: file nested too deep in directory structure"
*/

export const formatVenuePayload = (payload, isCreatedEntity) => {
  const creation_authorized_input_field = [
    'address',
    'bic',
    'bookingEmail',
    'city',
    'comment',
    'iban',
    'latitude',
    'longitude',
    'managingOffererId',
    'name',
    'postalCode',
    'publicName',
    'siret',
    'venueLabelId',
    'venueTypeId',
    'withdrawalDetails',
  ]

  const edition_authorized_input_field = [
    'address',
    'bookingEmail',
    'city',
    'comment',
    'isEmailAppliedOnAllOffers',
    'isWithdrawalAppliedOnAllOffers',
    'latitude',
    'longitude',
    'name',
    'postalCode',
    'publicName',
    'siret',
    'venueLabelId',
    'venueTypeId',
    'withdrawalDetails',
  ]

  const requestPayload = {}

  const authorizedFields = isCreatedEntity
    ? creation_authorized_input_field
    : edition_authorized_input_field

  authorizedFields.forEach(inputName => {
    if (payload[inputName] !== undefined) {
      requestPayload[inputName] = payload[inputName]
    } else if (inputName === 'venueTypeId' || inputName === 'venueLabelId') {
      requestPayload[inputName] = null
    }
  })

  return requestPayload
}
