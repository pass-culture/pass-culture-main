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
    'publicName',
    'postalCode',
    'siret',
    'venueTypeId',
  ]

  const edition_authorized_input_field = [
    'bookingEmail',
    'publicName',
    'address',
    'city',
    'comment',
    'latitude',
    'longitude',
    'name',
    'postalCode',
    'siret',
    'venueTypeId',
  ]

  const requestPayload = {}

  const authorizedFields = isCreatedEntity
    ? creation_authorized_input_field
    : edition_authorized_input_field

  authorizedFields.forEach(inputName => {
    if (payload[inputName]) {
      requestPayload[inputName] = payload[inputName]
    } else if (inputName === 'venueTypeId') {
      requestPayload[inputName] = null
    }
  })

  return requestPayload
}
