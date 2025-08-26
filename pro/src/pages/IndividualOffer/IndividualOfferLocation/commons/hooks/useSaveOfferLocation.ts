import type { UseFormSetError } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useNotification } from '@/commons/hooks/useNotification'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'

import type { LocationFormValues } from '../types'
import { toPatchOfferBodyModel } from '../utils/toPatchOfferBodyModel'

export function useSaveOfferLocation({
  offer,
  setError,
  withAddVideoFeatureFlag,
}: {
  offer: GetIndividualOfferResponseModel
  setError: UseFormSetError<LocationFormValues>
  withAddVideoFeatureFlag: boolean
}) {
  const { pathname } = useLocation()
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const notification = useNotification()
  const { mutate } = useSWRConfig()

  const isOnboarding = pathname.indexOf('onboarding') !== -1

  const saveAndContinue = async ({
    formValues,
    shouldSendMail = false,
  }: {
    formValues: LocationFormValues
    shouldSendMail?: boolean
  }) => {
    try {
      const requestBody = toPatchOfferBodyModel({
        offer,
        formValues,
        shouldSendMail,
      })

      await api.patchOffer(offer.id, requestBody)

      if (mode === OFFER_WIZARD_MODE.EDITION) {
        // Force offer update so that READ_ONLY page is up to date once the user is redirected
        await mutate([GET_OFFER_QUERY_KEY, offer.id])
      }

      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.USEFUL_INFORMATIONS
          : withAddVideoFeatureFlag
            ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA
            : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS

      navigate(
        getIndividualOfferUrl({
          offerId: offer.id,
          step: nextStep,
          mode:
            mode === OFFER_WIZARD_MODE.EDITION
              ? OFFER_WIZARD_MODE.READ_ONLY
              : mode,
          isOnboarding,
        })
      )
    } catch (error) {
      if (!isErrorAPIError(error)) {
        return
      }

      for (const field in error.body) {
        setError(field as keyof LocationFormValues, {
          message: error.body[field],
        })
      }

      notification.error(SENT_DATA_ERROR_MESSAGE)

      return
    }
  }

  return { saveAndContinue }
}
