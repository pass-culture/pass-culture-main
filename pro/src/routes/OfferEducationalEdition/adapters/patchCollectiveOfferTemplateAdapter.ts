import { api } from 'apiClient/api'
import { GetCollectiveOfferTemplateResponseModel } from 'apiClient/v1'
import { IOfferEducationalFormValues } from 'core/OfferEducational'

import { createPatchOfferPayload } from '../utils/createPatchOfferPayload'

export type Params = {
  offerId: string
  offer: IOfferEducationalFormValues
  initialValues: IOfferEducationalFormValues
}

type patchCollectiveOfferTemplateAdapter = Adapter<
  Params,
  GetCollectiveOfferTemplateResponseModel,
  null
>

export const patchCollectiveOfferTemplateAdapter: patchCollectiveOfferTemplateAdapter =
  async ({ offerId, offer, initialValues }) => {
    try {
      // the api returns no understandable error when the id is not valid, so we deal before calling the api
      if (!offerId || offerId === '')
        throw new Error('L’identifiant de l’offre n’est pas valide.')
      const payload = createPatchOfferPayload(offer, initialValues)
      const updatedOffer = await api.editCollectiveOfferTemplate(
        offerId,
        payload
      )

      return {
        isOk: true,
        message: 'Votre offre a bien été modifiée.',
        payload: updatedOffer,
      }
    } catch (error) {
      return {
        isOk: false,
        message: `Une erreur est survenue lors de la modification de votre offre.${
          // @ts-ignore
          error?.message ? ` ${error?.message}` : ''
        }`,
        payload: null,
      }
    }
  }
