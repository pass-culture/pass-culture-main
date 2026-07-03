import type { UseFormReturn } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { useSyncVenueCache } from '@/commons/hooks/useSyncVenueCache'

import {
  type VenueSettingsNotificationsFormValues,
  VenueSettingsNotificationsValidationSchema,
} from '../schemas'
import type { EditVenueBodyModelNotificationsPatch } from '../types'

export const useSave = ({
  form,
  venue,
}: {
  form: UseFormReturn<VenueSettingsNotificationsFormValues>
  venue: GetVenueResponseModel
}) => {
  const snackBar = useSnackBar()
  const { logEvent } = useAnalytics()
  const { syncVenueWithData } = useSyncVenueCache()

  const save = async (
    formValues: EditVenueBodyModelNotificationsPatch
  ): Promise<boolean> => {
    try {
      const updatedVenue = await api.editVenue({
        path: { venue_id: Number(venue.id) },
        body: VenueSettingsNotificationsValidationSchema.cast(formValues),
      })

      await syncVenueWithData(venue.id, updatedVenue)

      logEvent(Events.CLICKED_SAVE_VENUE, {
        saved: true,
        isEdition: true,
      })

      snackBar.success('Vos modifications ont été sauvegardées')

      return true
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
          form.setError(field as keyof VenueSettingsNotificationsFormValues, {
            type: field,
            message: formErrors[field]?.toString(),
          })
        }
      }

      logEvent(Events.CLICKED_SAVE_VENUE, {
        saved: false,
        isEdition: true,
      })

      return false
    }
  }

  return { save }
}
