import * as pcapi from 'repository/pcapi/pcapi'

export type PatchEducationalInstitutionAdapter = Adapter<
  {
    offerId: string
    institutionId: string
  },
  null,
  null
>

export const patchEducationalInstitutionAdapter: PatchEducationalInstitutionAdapter =
  async ({ offerId, institutionId }) => {
    try {
      await pcapi.patchEducationalInstitution(offerId, institutionId)

      return {
        isOk: true,
        message:
          'Les paramètres de visibilité de votre offre ont bien été enregistrés',
        payload: null,
      }
    } catch (e) {
      return {
        isOk: false,
        message:
          'Les paramètres de visibilité de votre offre n’ont pu être enregistrés',
        payload: null,
      }
    }
  }

export default patchEducationalInstitutionAdapter
