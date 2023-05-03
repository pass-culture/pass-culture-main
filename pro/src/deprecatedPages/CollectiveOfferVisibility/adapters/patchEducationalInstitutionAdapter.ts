import { api } from 'apiClient/api'
import { CollectiveOffer } from 'core/OfferEducational'

export type PatchEducationalInstitutionAdapter = Adapter<
  {
    offerId: number
    institutionId: string | null
    teacherEmail: string | null
  },
  CollectiveOffer,
  null
>

export const patchEducationalInstitutionAdapter: PatchEducationalInstitutionAdapter =
  async ({ offerId, institutionId, teacherEmail }) => {
    try {
      const collectiveOffer =
        await api.patchCollectiveOffersEducationalInstitution(offerId, {
          // @ts-expect-error string is not assignable to type number
          educationalInstitutionId: institutionId,
          teacherEmail,
        })

      return {
        isOk: true,
        message:
          'Les paramètres de visibilité de votre offre ont bien été enregistrés',
        payload: { ...collectiveOffer, isTemplate: false },
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
