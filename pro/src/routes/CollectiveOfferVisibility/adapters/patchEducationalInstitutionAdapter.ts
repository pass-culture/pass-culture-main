import * as pcapi from 'repository/pcapi/pcapi'

import { CollectiveOfferResponseModel } from 'core/OfferEducational'

export type PatchEducationalInstitutionAdapter = Adapter<
  {
    offerId: string
    institutionId: string
    isCreatingOffer: boolean
  },
  CollectiveOfferResponseModel,
  null
>

export const patchEducationalInstitutionAdapter: PatchEducationalInstitutionAdapter =
  async ({ offerId, institutionId, isCreatingOffer }) => {
    try {
      const collectiveOffer = await pcapi.patchEducationalInstitution(
        offerId,
        institutionId,
        isCreatingOffer
      )

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
