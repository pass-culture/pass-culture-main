import * as pcapi from 'repository/pcapi/pcapi'

import {
  computeActivationSuccessMessage,
  computeDeactivationSuccessMessage,
} from './utils'

type UpdateCollectiveOffersActiveStatusAdapter = Adapter<
  {
    ids: string[]
    isActive: boolean
  },
  null,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: '',
  payload: null,
}

export const updateCollectiveOffersActiveStatusAdapter: UpdateCollectiveOffersActiveStatusAdapter =
  async ({ ids, isActive }) => {
    const collectiveOfferIds = []
    const collectiveOfferTemplateIds = []

    for (const id of ids) {
      if (id.startsWith('T-')) {
        collectiveOfferTemplateIds.push(id.split('T-')[1])
      } else {
        collectiveOfferIds.push(id)
      }
    }

    try {
      await Promise.all([
        pcapi.patchIsCollectiveOfferActive(collectiveOfferIds, isActive),
        pcapi.patchIsTemplateOfferActive(collectiveOfferTemplateIds, isActive),
      ])

      return {
        isOk: true,
        message: isActive
          ? computeActivationSuccessMessage(ids.length)
          : computeDeactivationSuccessMessage(ids.length),
        payload: null,
      }
    } catch (error) {
      return {
        ...FAILING_RESPONSE,
        message: `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } des offres sélectionnées`,
      }
    }
  }
