import createDecorator from 'final-form-calculate'

import { getSireInfo, SIRET } from 'utils/sire'

const emptyValues = {
  address: null,
  city: null,
  latitude: null,
  longitude: null,
  name: null,
  postalCode: null,
}

export const createSiretDecorator = createDecorator({
  field: 'siret',
  updates: async siret => {
    const siretInfo = await getSireInfo(siret, SIRET)
    if (!siretInfo) return {}
    if (siretInfo.error) return emptyValues
    return siretInfo.values
  },
})

export default createSiretDecorator
