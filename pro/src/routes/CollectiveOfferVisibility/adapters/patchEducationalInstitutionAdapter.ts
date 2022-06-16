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
        message: 'L’institution a bien été rattachée à l’offre',
        payload: null,
      }
    } catch (e) {
      return {
        isOk: false,
        message:
          'Une erreur est survenue lors de l’enregistrement de l’institution',
        payload: null,
      }
    }
  }

export default patchEducationalInstitutionAdapter
