import { getSirenOrSiretInfo, SIRET } from '../../../../../../utils/siren'

const siretValidate = async siret => {
  const siretInfo = await getSirenOrSiretInfo(siret, SIRET)
  if (!siretInfo || !siretInfo.error) return undefined
  return siretInfo.error
}

export default siretValidate
