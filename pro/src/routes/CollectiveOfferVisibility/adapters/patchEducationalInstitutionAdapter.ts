import { GetCollectiveOfferResponseModel } from 'apiClient/v1'
import { api } from 'apiClient/api'

export type PatchEducationalInstitutionAdapter = Adapter<
  {
    offerId: string
    institutionId: string | null
    isCreatingOffer: boolean
  },
  GetCollectiveOfferResponseModel,
  null
>

export const patchEducationalInstitutionAdapter: PatchEducationalInstitutionAdapter =
  async ({ offerId, institutionId, isCreatingOffer }) => {
    try {
      const collectiveOffer =
        await api.patchCollectiveOffersEducationalInstitution(offerId, {
          // @ts-expect-error string is not assignable to type number
          educationalInstitutionId: institutionId,
          isCreatingOffer,
        })

      return {
        isOk: true,
        message:
          'Les paramètres de visibilité de votre offre ont bien été enregistrés',
        payload: collectiveOffer,
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
