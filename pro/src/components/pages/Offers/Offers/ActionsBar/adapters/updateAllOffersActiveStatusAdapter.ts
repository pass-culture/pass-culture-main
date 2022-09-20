import { api } from 'apiClient/api'
import { TSearchFilters } from 'core/Offers/types'
import { serializeApiFilters } from 'core/Offers/utils'

import {
  computeAllActivationSuccessMessage,
  computeAllDeactivationSuccessMessage,
} from './utils'

type UpdateAllOffersActiveStatusAdapter = Adapter<
  {
    searchFilters: Partial<TSearchFilters> & { isActive: boolean }
    nbSelectedOffers: number
  },
  null,
  null
>

const FAILING_RESPONSE: AdapterFailure<null> = {
  isOk: false,
  message: '',
  payload: null,
}

export const updateAllOffersActiveStatusAdapter: UpdateAllOffersActiveStatusAdapter =
  async ({ searchFilters, nbSelectedOffers }) => {
    const { isActive, ...filters } = searchFilters

    try {
      const payload = serializeApiFilters(filters)

      await api.patchAllOffersActiveStatus({
        ...payload,
        isActive,
      })

      return {
        isOk: true,
        message: isActive
          ? computeAllActivationSuccessMessage(nbSelectedOffers)
          : computeAllDeactivationSuccessMessage(nbSelectedOffers),
        payload: null,
      }
    } catch (error) {
      return {
        ...FAILING_RESPONSE,
        message: `Une erreur est survenue lors de ${
          isActive ? 'l’activation' : 'la désactivation'
        } des offres`,
      }
    }
  }
