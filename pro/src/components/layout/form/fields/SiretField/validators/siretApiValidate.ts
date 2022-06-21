import { getSiretDataAdapter } from 'core/Venue'

const siretApiValidate = async (siret: string): Promise<string | undefined> => {
  if (!siret) {
    return 'Ce champ est obligatoire'
  }

  const entrepriseData = await getSiretDataAdapter(siret)
  return entrepriseData.isOk ? undefined : entrepriseData.message
}

export default siretApiValidate
