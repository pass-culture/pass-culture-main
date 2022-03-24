import createDecorator from 'final-form-calculate'

import { getSiretDataAdapter } from 'core/Venue/adapters'

const emptyValues = {
  address: null,
  city: null,
  latitude: null,
  longitude: null,
  name: null,
  postalCode: null,
}

const bindGetSiretInformationToSiret = createDecorator({
  field: 'siret',
  updates: async siret => {
    const response = await getSiretDataAdapter(siret)
    if (!response.isOk) return emptyValues
    return response.payload.values
  },
})

export default bindGetSiretInformationToSiret
