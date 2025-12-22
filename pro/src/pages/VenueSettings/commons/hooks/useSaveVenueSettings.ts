import type { UseFormReturn } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'

import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useActiveFeature } from '@/commons/hooks/useActiveFeature'
import { useNotification } from '@/commons/hooks/useNotification'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'
import type { PartialBy } from '@/commons/utils/types'

import type { VenueSettingsFormContext } from '../types'
import { saveVenueSettings } from '../utils/saveVenueSettings'
import type { VenueSettingsFormValuesType } from '../validationSchema'

const removeVenueTypeFieldIf =
  (condition: boolean) =>
  (formValues: PartialBy<VenueSettingsFormValuesType, 'venueType'>) => {
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
  form: UseFormReturn<VenueSettingsFormValuesType>
  venue: GetVenueResponseModel
}) => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const isVenueActivityFeatureActive = useActiveFeature('WIP_VENUE_ACTIVITY')

  const saveAndContinue = async (
    formValues: PartialBy<VenueSettingsFormValuesType, 'venueType'>,
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

      const filteredFormValues = removeVenueTypeFieldIf(
        isVenueActivityFeatureActive && venue.isOpenToPublic
      )(formValues)

      await saveVenueSettings(filteredFormValues, formContext, { venue })

      navigate(getVenuePagePathToNavigateTo(venue.managingOfferer.id, venue.id))

      logEvent(Events.CLICKED_SAVE_VENUE, {
        from: location.pathname,
        saved: true,
        isEdition: true,
      })

      notify.success('Vos modifications ont été sauvegardées')
    } catch (error) {
      const formErrors = isErrorAPIError(error) ? error.body : {}
      const errorsKeys = Object.keys(formErrors)

      if (errorsKeys.length === 0 || errorsKeys.includes('global')) {
        notify.error('Erreur lors de la sauvegarde de la structure.')
      } else {
        notify.error(
          'Une ou plusieurs erreurs sont présentes dans le formulaire'
        )

        for (const field of errorsKeys) {
          form.setError(field as keyof VenueSettingsFormValuesType, {
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
