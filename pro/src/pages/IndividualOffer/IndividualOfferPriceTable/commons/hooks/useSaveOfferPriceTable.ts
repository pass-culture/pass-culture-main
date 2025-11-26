import type { UseFormReturn } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'

import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useNotification } from '@/commons/hooks/useNotification'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { getSuccessMessage } from '@/pages/IndividualOffer/commons/getSuccessMessage'

import { FAILED_PATCH_OFFER_USER_MESSAGE } from '../constants'
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
            ? INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE
            : INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS,
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
      if (form.formState.isDirty) {
        if (offer.isEvent) {
          await saveEventOfferPriceTable(formValues, form, { offer })
        } else {
          await saveNonEventOfferPriceTable(formValues, form, {
            offer,
          })
        }
      }

      if (mode === OFFER_WIZARD_MODE.EDITION) {
        notify.success(getSuccessMessage(mode))
      }

      navigate(nextStepUrl)
    } catch (error) {
      if (isErrorAPIError(error)) {
        const serializedApiErrors = serializeApiErrors(error.body)
        Object.entries(serializedApiErrors).forEach(([key, value], index) => {
          const message = typeof value === 'string' ? value : value?.join(',  ')
          const formKey = `entries.${index}.${key}`
          form.setError(formKey as keyof PriceTableFormValues, {
            message,
          })
        })

        if (serializedApiErrors.priceLimitationRule) {
          form.setError('entries.0.price', {
            type: 'custom',
            message: 'Non valide',
          })
        }
      }

      return notify.error(FAILED_PATCH_OFFER_USER_MESSAGE)
    }
  }

  return { saveAndContinue }
}
