import type { UseFormReturn } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'

import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import type { GetIndividualOfferResponseModelV2 } from '@/apiClient/v1'
import {
  INDIVIDUAL_OFFER_WIZARD_STEP_IDS,
  OFFER_WIZARD_MODE,
} from '@/commons/core/Offers/constants'
import { getIndividualOfferUrl } from '@/commons/core/Offers/utils/getIndividualOfferUrl'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useOfferWizardMode } from '@/commons/hooks/useOfferWizardMode'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'
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
  offer: GetIndividualOfferResponseModelV2
}) => {
  const mode = useOfferWizardMode()
  const navigate = useNavigate()
  const { pathname } = useLocation()
  const snackBar = useSnackBar()
  const { syncVenue } = useSyncVenueCache()
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')

  const isOnboarding = pathname.includes('onboarding')

  const saveAndContinue = async (
    formValues: PriceTableFormValues
  ): Promise<void> => {
    let nextStep = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.PRACTICAL_INFOS

    if (mode === OFFER_WIZARD_MODE.EDITION) {
      nextStep = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TARIFS
    } else if (offer.isEvent) {
      nextStep = INDIVIDUAL_OFFER_WIZARD_STEP_IDS.TIMETABLE
    }

    const nextStepUrl = getIndividualOfferUrl({
      offerId: offer.id,
      step: nextStep,
      mode:
        mode === OFFER_WIZARD_MODE.EDITION ? OFFER_WIZARD_MODE.READ_ONLY : mode,
      isOnboarding,
      isOfferExposureEnabled,
    })

    if (!form.formState.isDirty && mode === OFFER_WIZARD_MODE.EDITION) {
      navigate(nextStepUrl)

      snackBar.success(getSuccessMessage(mode))

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

      await syncVenue(offer.venue.id)

      form.reset(formValues)

      if (mode === OFFER_WIZARD_MODE.EDITION) {
        if (isOfferExposureEnabled) {
          snackBar.success('Votre offre a bien été modifiée.')
        } else {
          snackBar.success(getSuccessMessage(mode))
        }
      }

      navigate(nextStepUrl)
    } catch (error) {
      if (isErrorAPIError(error)) {
        serializeApiErrors(error.body, form.setError)
      }

      return snackBar.error(FAILED_PATCH_OFFER_USER_MESSAGE)
    }
  }

  return { saveAndContinue }
}
