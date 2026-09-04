import { useId, useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import type {
  GetVenueResponseModel,
  PostVenueProviderBody,
  VenueProviderResponse,
} from '@/apiClient/v1'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { isSelectedPartnerOrOffererClosed } from '@/commons/utils/isSelectedPartnerOrOffererClosed'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import { DetailedModal } from '@/design-system/DetailedModal/DetailedModal'
import fullEditIcon from '@/icons/full-edit.svg'

import {
  GenericCinemaProviderForm,
  type GenericCinemaProviderFormValues,
} from '../GenericCinemaProviderForm/GenericCinemaProviderForm'
import styles from './GenericCinemaProviderEdit.module.scss'

export interface GenericCinemaProviderEditProps {
  venueProvider: VenueProviderResponse
  venue: GetVenueResponseModel
  showAdvancedFields: boolean
}

export const GenericCinemaProviderEdit = ({
  venueProvider,
  venue,
  showAdvancedFields = false,
}: GenericCinemaProviderEditProps): JSX.Element => {
  const snackBar = useSnackBar()
  const { mutate } = useSWRConfig()
  const cinemaProviderFormId = useId()
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const isClosed = isSelectedPartnerOrOffererClosed(venue)

  const editVenueProvider = async (
    payload: PostVenueProviderBody
  ): Promise<boolean> => {
    try {
      await api.updateVenueProvider({
        path: { venue_provider_id: venueProvider.id },
        body: {
          // we must get rid of payload.providerId
          price: payload.price,
          isActive: payload.isActive,
          isDuo: payload.isDuo,
          quantity: payload.quantity,
          venueIdAtOfferProvider: payload.venueIdAtOfferProvider,
        },
      })

      await mutate([GET_VENUE_PROVIDERS_QUERY_KEY, venue.id])
      snackBar.success(
        "Les modifications ont bien été importées et s'appliqueront aux nouvelles séances créées."
      )
      return true
    } catch {
      snackBar.error('Une erreur s’est produite, veuillez réessayer')
      return false
    }
  }

  const onConfirmDialog = async (
    payload: PostVenueProviderBody
  ): Promise<boolean> => {
    setIsDialogOpen(false)

    const isSuccess = await editVenueProvider({
      ...payload,
      isActive: venueProvider.isActive,
    })

    return isSuccess
  }

  const initialValues: GenericCinemaProviderFormValues = {
    price: venueProvider.price,
    quantity: venueProvider.quantity,
    isDuo: venueProvider.isDuo ?? false,
    isActive: venueProvider.isActive,
  }

  return (
    <>
      <Button
        variant={ButtonVariant.TERTIARY}
        color={ButtonColor.NEUTRAL}
        icon={fullEditIcon}
        label="Paramétrer"
        disabled={isClosed}
        onClick={() => setIsDialogOpen(true)}
      />

      <DetailedModal
        isOpen={isDialogOpen}
        onClose={() => setIsDialogOpen(false)}
        title="Modifier les paramètres de vos offres"
        primaryAction={
          <Button type="submit" form={cinemaProviderFormId} label="Modifier" />
        }
        secondaryAction={
          <Button
            type="button"
            variant={ButtonVariant.SECONDARY}
            color={ButtonColor.NEUTRAL}
            onClick={() => setIsDialogOpen(false)}
            label="Annuler"
          />
        }
        isFooterFixed
      >
        <div className={styles['cinema-provider-form-dialog']}>
          <GenericCinemaProviderForm
            isCreationMode={false}
            showAdvancedFields={showAdvancedFields}
            initialValues={initialValues}
            saveVenueProvider={onConfirmDialog}
            providerId={venueProvider.provider.id}
            formId={cinemaProviderFormId}
            showFooter={false}
          />
        </div>
      </DetailedModal>
    </>
  )
}
