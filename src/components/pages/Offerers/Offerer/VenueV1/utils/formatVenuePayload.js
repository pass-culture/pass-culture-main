/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 */

const creation_authorized_input_field = [
  'address',
  'bic',
  'bookingEmail',
  'city',
  'comment',
  'description',
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
  'audioDisabilityCompliant',
  'mentalDisabilityCompliant',
  'motorDisabilityCompliant',
  'visualDisabilityCompliant',
]

const edition_authorized_input_field = [
  'address',
  'bookingEmail',
  'city',
  'comment',
  'description',
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
  'audioDisabilityCompliant',
  'mentalDisabilityCompliant',
  'motorDisabilityCompliant',
  'visualDisabilityCompliant',
]

export const formatVenuePayload = (payload, isCreatedEntity) => {
  const requestPayload = {}

  const authorizedFields = isCreatedEntity
    ? creation_authorized_input_field
    : edition_authorized_input_field

  authorizedFields.forEach(inputName => {
    /* @debt implementation "Gaël : this is a hack to submit empty strings. react-final-form treat them as undefined and do not submit undefined values. see https://github.com/final-form/react-final-form/issues/130 "*/
    if (inputName === 'description' && payload[inputName] === undefined) {
      payload[inputName] = ''
    }

    if (payload[inputName] !== undefined) {
      requestPayload[inputName] = payload[inputName]
    } else if (inputName === 'venueTypeId' || inputName === 'venueLabelId') {
      requestPayload[inputName] = null
    }
  })

  return requestPayload
}
