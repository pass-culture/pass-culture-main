import { isError } from 'apiClient/helpers'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared/constants'
import getSiretData from 'core/Venue/getSiretData'

const siretApiValidate = async (siret: string): Promise<string | undefined> => {
  if (!siret) {
    return 'Ce champ est obligatoire'
  }

  try {
    await getSiretData(siret)
    return undefined
  } catch (e) {
    return isError(e) ? e.message : GET_DATA_ERROR_MESSAGE
  }
}

export default siretApiValidate
