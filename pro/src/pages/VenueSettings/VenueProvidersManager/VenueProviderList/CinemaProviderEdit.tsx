import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { GetVenueResponseModel, VenueProviderResponse } from 'apiClient/v1'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useNotification } from 'commons/hooks/useNotification'
import fullEditIcon from 'icons/full-edit.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

import { CinemaProviderFormDialog } from './CinemaProviderFormDialog'
import { CinemaProviderParametersValues } from './types'

export interface CinemaProviderEditProps {
  venueProvider: VenueProviderResponse
  venue: GetVenueResponseModel
  offererId: number
}

export const CinemaProviderEdit = ({
  venueProvider,
  venue,
  offererId,
}: CinemaProviderEditProps): JSX.Element => {
  const notification = useNotification()
  const { mutate } = useSWRConfig()

  const editVenueProvider = async (
    payload: CinemaProviderParametersValues
  ): Promise<boolean> => {
    try {
      await api.updateVenueProvider(payload)

      await mutate([GET_VENUE_PROVIDERS_QUERY_KEY, venue.id])
      notification.success(
        "Les modifications ont bien été importées et s'appliqueront aux nouvelles séances créées."
      )
      return true
    } catch {
      notification.error('Une erreur s’est produite, veuillez réessayer')
      return false
    }
  }

  const onConfirmDialog = async (
    payload: CinemaProviderParametersValues
  ): Promise<boolean> => {
    const isSuccess = await editVenueProvider({
      ...payload,
      isActive: venueProvider.isActive,
    })

    return isSuccess
  }

  const initialValues = {
    isDuo: venueProvider.isDuo,
  }

  return (
    <DialogBuilder
      variant="drawer"
      title="Modifier les paramètres de vos offres"
      trigger={
        <Button variant={ButtonVariant.TERNARY} icon={fullEditIcon}>
          Paramétrer
        </Button>
      }
    >
      <CinemaProviderFormDialog
        initialValues={initialValues}
        onConfirm={onConfirmDialog}
        providerId={venueProvider.provider.id}
        venueId={venueProvider.venueId}
        offererId={offererId}
      />
    </DialogBuilder>
  )
}
