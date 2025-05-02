import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { getHumanReadableApiError } from 'apiClient/helpers'
import {
  GetVenueResponseModel,
  PostVenueProviderBody,
  VenueProviderResponse,
} from 'apiClient/v1'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from 'commons/config/swrQueryKeys'
import { useNotification } from 'commons/hooks/useNotification'
import fullEditIcon from 'icons/full-edit.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { DialogBuilder } from 'ui-kit/DialogBuilder/DialogBuilder'

import {
  AllocineProviderForm,
  FormValuesProps,
} from '../AllocineProviderForm/AllocineProviderForm'

import styles from './AllocineProviderEdit.module.scss'

export interface AllocineProviderEditProps {
  venueProvider: VenueProviderResponse
  venue: GetVenueResponseModel
  offererId: number
}

export const AllocineProviderEdit = ({
  venueProvider,
  venue,
  offererId,
}: AllocineProviderEditProps): JSX.Element => {
  const notification = useNotification()
  const { mutate } = useSWRConfig()

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
    } catch (error) {
      notification.error(getHumanReadableApiError(error))
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

    return isSuccess
  }

  const initialValues: FormValuesProps = {
    price: venueProvider.price ? venueProvider.price : '',
    quantity: venueProvider.quantity ? Number(venueProvider.quantity) : '',
    isDuo: venueProvider.isDuo ?? false,
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
      <div className={styles['allocine-provider-form']}>
        <div className={styles['explanation']}>
          Les modifications s’appliqueront uniquement aux nouvelles offres
          créées. La modification doit être faite manuellement pour les offres
          existantes.
        </div>
        <AllocineProviderForm
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
