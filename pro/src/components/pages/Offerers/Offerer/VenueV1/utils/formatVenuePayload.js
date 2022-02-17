const creation_authorized_input_field = [
  'address',
  'bic',
  'bookingEmail',
  'businessUnitId',
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
  'venueTypeCode',
  'withdrawalDetails',
  'audioDisabilityCompliant',
  'mentalDisabilityCompliant',
  'motorDisabilityCompliant',
  'visualDisabilityCompliant',
  'contact',
]

const edition_authorized_input_field = [
  'address',
  'bookingEmail',
  'businessUnitId',
  'city',
  'comment',
  'description',
  'isAccessibilityAppliedOnAllOffers',
  'isEmailAppliedOnAllOffers',
  'isWithdrawalAppliedOnAllOffers',
  'latitude',
  'longitude',
  'name',
  'postalCode',
  'publicName',
  'siret',
  'venueLabelId',
  'venueTypeCode',
  'withdrawalDetails',
  'audioDisabilityCompliant',
  'mentalDisabilityCompliant',
  'motorDisabilityCompliant',
  'visualDisabilityCompliant',
  'contact',
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

    if (inputName === 'contact' && payload[inputName]?.phoneNumber === '') {
      payload[inputName].phoneNumber = null
    }

    if (inputName === 'contact' && payload[inputName]?.email === '') {
      payload[inputName].email = null
    }

    if (inputName === 'contact' && payload[inputName]?.website === '') {
      payload[inputName].website = null
    }

    if (payload[inputName] !== undefined) {
      requestPayload[inputName] = payload[inputName]
    } else if (inputName === 'venueTypeCode' || inputName === 'venueLabelId') {
      requestPayload[inputName] = null
    }
  })

  return requestPayload
}
