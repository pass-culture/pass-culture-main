/*
* @debt complexity "Gaël: file nested too deep in directory structure"
*/

import { getSiretInformations } from '../../../siret/selectSiretInformations'

const siretValidate = async siret => {
  const siretInfo = await getSiretInformations(siret)
  if (!siretInfo || !siretInfo.error) return undefined
  return siretInfo.error
}

export default siretValidate
