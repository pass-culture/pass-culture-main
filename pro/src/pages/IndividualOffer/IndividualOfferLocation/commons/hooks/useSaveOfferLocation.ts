import { useRef } from 'react'
import type { UseFormSetError } from 'react-hook-form'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { useSnackBar } from '@/commons/hooks/useSnackBar'

import type { LocationFormValues } from '../types'
import { toPatchOfferBodyModel } from '../utils/toPatchOfferBodyModel'

type SaveOfferLocationHandler = (params: {
  formValues: LocationFormValues
  shouldSendMail?: boolean
}) => Promise<boolean>

export function useSaveOfferLocation({
  offer,
  setError,
}: {
  offer: GetIndividualOfferResponseModel
  setError: UseFormSetError<LocationFormValues>
}): {
  save: SaveOfferLocationHandler
  /** Set on a successful edition save; read by `afterSubmitState` so the
   * message is shown once the destination page has taken over. */
  hasSavedRef: React.RefObject<boolean>
} {
  const mode = useOfferWizardMode()
  const snackBar = useSnackBar()
  const { mutate } = useSWRConfig()
  const hasSavedRef = useRef(false)

  const save: SaveOfferLocationHandler = async ({
    formValues,
    shouldSendMail = false,
  }) => {
    try {
      const requestBody = toPatchOfferBodyModel({
        offer,
        formValues,
        shouldSendMail,
      })

      await mutate(
        [GET_OFFER_QUERY_KEY, offer.id],
        api.patchOffer({ path: { offer_id: offer.id }, body: requestBody }),
        { revalidate: false }
      )

      if (mode === OFFER_WIZARD_MODE.EDITION) {
        hasSavedRef.current = true
      }

      return true
    } catch (error) {
      if (isErrorAPIError(error)) {
        for (const field in error.body) {
          setError(field as keyof LocationFormValues, {
            message: error.body[field],
          })
        }

        snackBar.error(SENT_DATA_ERROR_MESSAGE)
      }

      return false
    }
  }

  return { save, hasSavedRef }
}
