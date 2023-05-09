import { api } from 'apiClient/api'

import {
  computeDeletionErrorMessage,
  computeDeletionSuccessMessage,
} from './utils'

type UpdateAllCollectiveOffersActiveStatusAdapter = Adapter<
  {
    ids: string[]
    nbSelectedOffers?: number
  },
  null,
  null
>

export const deleteDraftOffersAdapter: UpdateAllCollectiveOffersActiveStatusAdapter =
  async ({ ids, nbSelectedOffers = 1 }) => {
    try {
      await api.deleteDraftOffers({
        // @ts-expect-error type string[] is not assignable to type number[]
        ids,
      })

      return {
        isOk: true,
        message: computeDeletionSuccessMessage(nbSelectedOffers),
        payload: null,
      }
    } catch (error) {
      return {
        isOk: false,
        payload: null,
        message: computeDeletionErrorMessage(nbSelectedOffers),
      }
    }
  }
