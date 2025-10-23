import type { UseFormReturn } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router'

import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useNotification } from '@/commons/hooks/useNotification'
import { getVenuePagePathToNavigateTo } from '@/commons/utils/getVenuePagePathToNavigateTo'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../types'
import { saveVenueSettings } from '../utils/saveVenueSettings'

export const useSaveVenueSettings = ({
  form,
  venue,
}: {
  form: UseFormReturn<VenueSettingsFormValues>
  venue: GetVenueResponseModel
}) => {
  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotification()
  const { logEvent } = useAnalytics()

  const saveAndContinue = async (
    formValues: VenueSettingsFormValues,
    formContext: VenueSettingsFormContext
  ) => {
    try {
      await saveVenueSettings(formValues, formContext, { venue })

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
