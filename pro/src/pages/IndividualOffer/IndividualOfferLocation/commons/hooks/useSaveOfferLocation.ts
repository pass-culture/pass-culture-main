import type { UseFormSetError } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import { apiNew } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetIndividualOfferResponseModel } from '@/apiClient/v1/new'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { SENT_DATA_ERROR_MESSAGE } from '@/commons/core/shared/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { useSnackBar } from '@/commons/hooks/useSnackBar'

import type { LocationFormValues } from '../types'
import { toPatchOfferBodyModel } from '../utils/toPatchOfferBodyModel'

export function useSaveOfferLocation({
  offer,
  setError,
}: {
  offer: GetIndividualOfferResponseModel
  setError: UseFormSetError<LocationFormValues>
}) {
  const { pathname } = useLocation()
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const snackBar = useSnackBar()
  const { mutate } = useSWRConfig()
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')

  const isOnboarding = pathname.includes('onboarding')

  const saveAndContinue = async ({
    formValues,
    shouldSendMail = false,
    closeDialog,
  }: {
    formValues: LocationFormValues
    shouldSendMail?: boolean
    closeDialog: () => void
  }) => {
    try {
      const requestBody = toPatchOfferBodyModel({
        offer,
        formValues,
        shouldSendMail,
      })

      await mutate(
        [GET_OFFER_QUERY_KEY, offer.id],
        apiNew.patchOffer({ path: { offer_id: offer.id }, body: requestBody }),
        { revalidate: false }
      )

      if (isOfferExposureEnabled && mode === OFFER_WIZARD_MODE.EDITION) {
        snackBar.success('Votre offre a bien été modifiée.')
        closeDialog()
      }

      const nextStep =
        mode === OFFER_WIZARD_MODE.EDITION
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.LOCATION
          : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.MEDIA

      if (!isOfferExposureEnabled || mode === OFFER_WIZARD_MODE.CREATION) {
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
      }
    } catch (error) {
      if (!isErrorAPIError(error)) {
        return
      }

      for (const field in error.body) {
        setError(field as keyof LocationFormValues, {
          message: error.body[field],
        })
      }

      snackBar.error(SENT_DATA_ERROR_MESSAGE)

      return
    }
  }

  return { saveAndContinue }
}
