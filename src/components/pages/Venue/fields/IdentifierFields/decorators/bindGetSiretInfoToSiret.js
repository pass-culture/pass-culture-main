import createDecorator from 'final-form-calculate'

import { getSirenOrSiretInfo, SIRET } from '../../../../../../utils/siren'

const emptyValues = {
  address: null,
  city: null,
  latitude: null,
  longitude: null,
  name: null,
  postalCode: null,
}

const bindGetSiretInfoToSiret = createDecorator({
  field: 'siret',
  updates: async siret => {
    const siretInfo = await getSirenOrSiretInfo(siret, SIRET)
    if (!siretInfo) return {}
    if (siretInfo.error) return emptyValues
    return siretInfo.values
  },
})

export default bindGetSiretInfoToSiret
