import { isError } from '@/apiClient//helpers'
import { GET_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { getSiretData } from '@/commons/core/Venue/getSiretData'

export const siretApiValidate = async (
  siret: string
): Promise<string | null> => {
  if (!siret) {
    return 'Ce champ est obligatoire'
  }

  try {
    await getSiretData(siret)
    return null
  } catch (e) {
    return isError(e) ? e.message : GET_DATA_ERROR_MESSAGE
  }
}
