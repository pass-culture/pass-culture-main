import createDecorator from 'final-form-calculate'

import { getSirenDataAdapter } from 'core/Offerers/adapters'

export const sirenUpdate = async humanSiren => {
  const response = await getSirenDataAdapter(humanSiren)
  if (!response.isOk)
    return {
      address: '',
      city: '',
      name: '',
      postalCode: '',
      siren: humanSiren,
    }
  return response.payload.values
}

export const addressAndDesignationFromSirenDecorator = createDecorator({
  field: 'siren',
  updates: sirenUpdate,
})
