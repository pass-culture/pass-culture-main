import { getSireInfo, SIRET } from 'utils/siren'

export const siretValidate = async siret => {
  const siretInfo = await getSireInfo(siret, SIRET)
  if (!siretInfo || !siretInfo.error) return undefined
  return siretInfo.error
}

export default siretValidate
