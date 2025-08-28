import type { UseFormReturn } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'
import { useSWRConfig } from 'swr'

import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { GET_OFFER_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useNotification } from '@/commons/hooks/useNotification'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { getSuccessMessage } from '@/components/IndividualOffer/utils/getSuccessMessage'

import type { PriceTableFormValues } from '../schemas'
import { saveEventOfferPriceTable } from '../utils/saveEventOfferPriceTable'
import { saveNonEventOfferPriceTable } from '../utils/saveNonEventOfferPriceTable'

export const useSaveOfferPriceTable = ({
  form,
  offer,
}: {
  form: UseFormReturn<PriceTableFormValues>
  offer: GetIndividualOfferWithAddressResponseModel
}) => {
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const notify = useNotification()
  const { mutate } = useSWRConfig()

  const isOnboarding = pathname.indexOf('onboarding') !== -1

  const saveAndContinue = async (
    formValues: PriceTableFormValues
  ): Promise<void> => {
    const nextStepUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step:
        mode === OFFER_WIZARD_MODE.EDITION
          ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS
          : offer.isEvent
            ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.STOCKS
            : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.SUMMARY,
      mode:
        mode === OFFER_WIZARD_MODE.EDITION ? OFFER_WIZARD_MODE.READ_ONLY : mode,
      isOnboarding,
    })

    if (!form.formState.isDirty && mode === OFFER_WIZARD_MODE.EDITION) {
      navigate(nextStepUrl)

      notify.success(getSuccessMessage(mode))

      return
    }

    try {
      if (offer.isEvent) {
        await saveEventOfferPriceTable(formValues, { offer })
      } else {
        await saveNonEventOfferPriceTable(formValues, {
          offer,
          setError: form.setError,
        })
      }
    } catch (error) {
      if (error instanceof Error) {
        notify.error(error.message)
      }
      return
    }

    await mutate([GET_OFFER_QUERY_KEY, offer.id])

    if (mode === OFFER_WIZARD_MODE.EDITION) {
      notify.success(getSuccessMessage(mode))
    }

    navigate(nextStepUrl)
  }

  return { saveAndContinue }
}
