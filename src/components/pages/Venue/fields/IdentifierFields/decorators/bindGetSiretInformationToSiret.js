import createDecorator from 'final-form-calculate'

import { getSiretInformations } from '../../../siret/selectSiretInformations'

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
    const siretInfo = await getSiretInformations(siret)
    if (!siretInfo) return {}
    if (siretInfo.error) return emptyValues
    return siretInfo.values
  },
})

export default bindGetSiretInformationToSiret
