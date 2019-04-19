export const VENUE_EDIT_PATCH_KEYS = ['bookingEmail', 'name', 'publicName']

export const VENUE_NEW_PATCH_KEYS = [
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
]

export const OFFERER_NEW_PATCH_KEYS = [
  'address',
  'city',
  'name',
  'siren',
  'postalCode',
]

export const OFFERER_EDIT_PATCH_KEYS = ['bic', 'iban', 'rib']

export const formatPatch = (
  patch,
  config,
  newFormKeys,
  editFormPermittedKeys
) => {
  const { isNew } = config || {}
  const formPatch = {}

  let patchKeys = editFormPermittedKeys
  if (isNew) {
    patchKeys = newFormKeys
  }

  patchKeys.forEach(key => {
    if (patch[key]) {
      formPatch[key] = patch[key]
    }
  })
  return formPatch
}
