import { getSiretInformations } from '../../../siret/siretInformations'

const siretValidate = async siret => {
  const siretInfo = await getSiretInformations(siret)
  if (!siretInfo || !siretInfo.error) return undefined
  return siretInfo.error
}

export default siretValidate
