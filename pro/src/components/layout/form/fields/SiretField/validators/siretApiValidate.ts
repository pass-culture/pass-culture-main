import { getEntrepriseData } from 'core/Venue'

const siretApiValidate = async (
  siret: string,
  comment: string
): Promise<string | undefined> => {
  if (!siret) {
    return comment ? undefined : 'Ce champs est obligatoire'
  }

  const entrepriseData = await getEntrepriseData(siret)
  return entrepriseData.isOk ? undefined : entrepriseData.message
}

export default siretApiValidate
