import { getSirenOrSiretInfo, SIRET } from '../../../../../../utils/siren'

export const siretValidate = async siret => {
  const siretInfo = await getSirenOrSiretInfo(siret, SIRET)
  if (!siretInfo || !siretInfo.error) return undefined
  return siretInfo.error
}

export default siretValidate
