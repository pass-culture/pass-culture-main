import { useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient//api'
import {
  GetVenueResponseModel,
  PostVenueProviderBody,
  VenueProviderResponse,
} from '@/apiClient//v1'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useNotification } from '@/commons/hooks/useNotification'
import fullEditIcon from '@/icons/full-edit.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { DialogBuilder } from '@/ui-kit/DialogBuilder/DialogBuilder'

import {
  GenericCinemaProviderForm,
  GenericCinemaProviderFormValues,
} from '../GenericCinemaProviderForm/GenericCinemaProviderForm'
import styles from './GenericCinemaProviderEdit.module.scss'

export interface GenericCinemaProviderEditProps {
  venueProvider: VenueProviderResponse
  venue: GetVenueResponseModel
  offererId: number
  showAdvancedFields: boolean
}

export const GenericCinemaProviderEdit = ({
  venueProvider,
  venue,
  offererId,
  showAdvancedFields = false,
}: GenericCinemaProviderEditProps): JSX.Element => {
  const notification = useNotification()
  const { mutate } = useSWRConfig()
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const editVenueProvider = async (
    payload: PostVenueProviderBody
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
    payload: PostVenueProviderBody
  ): Promise<boolean> => {
    const isSuccess = await editVenueProvider({
      ...payload,
      isActive: venueProvider.isActive,
    })

    setIsDialogOpen(false)

    return isSuccess
  }

  const initialValues: GenericCinemaProviderFormValues = {
    price: venueProvider.price,
    quantity: venueProvider.quantity,
    isDuo: venueProvider.isDuo ?? false,
    isActive: venueProvider.isActive,
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
      open={isDialogOpen}
      onOpenChange={setIsDialogOpen}
    >
      <div className={styles['cinema-provider-form-dialog']}>
        <div className={styles['explanation']}>
          Les modifications s’appliqueront uniquement aux nouvelles offres
          créées. La modification doit être faite manuellement pour les offres
          existantes.
        </div>
        <GenericCinemaProviderForm
          showAdvancedFields={showAdvancedFields}
          initialValues={initialValues}
          saveVenueProvider={onConfirmDialog}
          providerId={venueProvider.provider.id}
          venueId={venueProvider.venueId}
          offererId={offererId}
        />
      </div>
    </DialogBuilder>
  )
}
