import { getSireInfo, SIRET } from 'utils/sire'

export const validateSiret = async siret => {
  const siretInfo = await getSireInfo(siret, SIRET)
  if (!siretInfo || !siretInfo.error) return undefined
  return siretInfo.error
}

export default validateSiret
