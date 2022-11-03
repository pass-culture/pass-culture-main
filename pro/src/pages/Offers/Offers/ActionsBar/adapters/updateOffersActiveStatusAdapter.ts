import { api } from 'apiClient/api'

import {
  computeActivationSuccessMessage,
  computeDeactivationSuccessMessage,
} from './utils'

type UpdateOffersActiveStatusAdapter = Adapter<
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

export const updateOffersActiveStatusAdapter: UpdateOffersActiveStatusAdapter =
  async ({ ids, isActive }) => {
    try {
      // @ts-expect-error: type string is not assignable to type number
      await api.patchOffersActiveStatus({ ids, isActive })

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
