import type { UseFormReturn } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'

import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'

import type {
  PartialBy,
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../types'
import { saveVenueSettings } from '../utils/saveVenueSettings'

const removeVenueTypeFieldIf =
  (condition: boolean) =>
  (formValues: PartialBy<VenueSettingsFormValues, 'venueType'>) => {
    const { venueType: _, ...props } = formValues
    if (condition) {
      return props
    }
    return formValues
  }

export const useSaveVenueSettings = ({
  form,
  venue,
}: {
  form: UseFormReturn<VenueSettingsFormValues>
  venue: GetVenueResponseModel
}) => {
  const navigate = useNavigate()
  const location = useLocation()
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()

  const saveAndContinue = async (
    formValues: PartialBy<VenueSettingsFormValues, 'venueType'>,
    formContext: VenueSettingsFormContext
  ) => {
    try {
      /*
        If WIP_VENUE_ACTIVITY is activated, then the "venueType" field is made conditional.
        Condition is:
          If venue is `openToPublic`, then the "venueType" field isn't handled in this form anymore,
          so we need to EXPLICITLY ignore the value here.

        (Else, We still update the "venueType" in this form)
      */

      const filteredFormValues = removeVenueTypeFieldIf(venue.isOpenToPublic)(
        formValues
      )

      await saveVenueSettings(filteredFormValues, formContext, { venue })

      navigate(getVenuePagePathToNavigateTo(venue.managingOfferer.id, venue.id))

      logEvent(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: true,
        isEdition: true,
      })

      snackBar.success('Vos modifications ont été sauvegardées')
    } catch (error) {
      const formErrors = isErrorAPIError(error) ? error.body : {}
      const errorsKeys = Object.keys(formErrors)

      if (errorsKeys.length === 0 || errorsKeys.includes('global')) {
        snackBar.error('Erreur lors de la sauvegarde de la structure.')
      } else {
        snackBar.error(
          'Une ou plusieurs erreurs sont présentes dans le formulaire'
        )

        for (const field of errorsKeys) {
          form.setError(field as keyof VenueSettingsFormValues, {
            type: field,
            message: formErrors[field]?.toString(),
          })
        }
      }

      logEvent(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: false,
        isEdition: true,
      })
    }
  }

  return { saveAndContinue }
}
