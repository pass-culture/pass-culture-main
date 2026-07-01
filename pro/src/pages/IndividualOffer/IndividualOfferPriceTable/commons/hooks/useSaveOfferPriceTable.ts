import type { UseFormReturn } from 'react-hook-form'

import { isErrorAPIError, serializeApiErrors } from '@/apiClient/helpers'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1'
import { OFFER_WIZARD_MODE } from '@/commons/core/Offers/constants'
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
  offer: GetIndividualOfferWithAddressResponseModel
}): {
  save: (formValues: PriceTableFormValues) => Promise<boolean>
} => {
  const mode = useOfferWizardMode()
  const snackBar = useSnackBar()
  const { syncVenue } = useSyncVenueCache()
  const isOfferExposureEnabled = useActiveFeature('WIP_OFFER_EXPOSURE')

  const save = async (formValues: PriceTableFormValues): Promise<boolean> => {
    if (!form.formState.isDirty && mode === OFFER_WIZARD_MODE.EDITION) {
      snackBar.success(getSuccessMessage(mode))

      return true
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
        snackBar.success(
          isOfferExposureEnabled
            ? 'Votre offre a bien été modifiée.'
            : getSuccessMessage(mode)
        )
      }

      return true
    } catch (error) {
      if (isErrorAPIError(error)) {
        serializeApiErrors(error.body, form.setError)
      }

      snackBar.error(FAILED_PATCH_OFFER_USER_MESSAGE)

      return false
    }
  }

  return { save }
}
