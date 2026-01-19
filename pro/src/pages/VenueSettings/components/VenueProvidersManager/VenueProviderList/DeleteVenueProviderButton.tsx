import { useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import type { GetVenueResponseModel } from '@/apiClient/v1'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullTrashIcon from '@/icons/full-trash.svg'

import { DeleteVenueProviderDialog } from './DeleteVenueProviderDialog'

interface DeleteVenueProviderButtonProps {
  venueProviderId: number
  venue: GetVenueResponseModel
  selectSoftwareButtonRef: React.RefObject<HTMLButtonElement>
}

export const DeleteVenueProviderButton = ({
  venueProviderId,
  venue,
  selectSoftwareButtonRef,
}: DeleteVenueProviderButtonProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const snackBar = useSnackBar()
  const { mutate } = useSWRConfig()

  const tryToDeleteVenueProvider = async () => {
    setIsLoading(true)
    try {
      await api.deleteVenueProvider(venueProviderId)

      await mutate([GET_VENUE_PROVIDERS_QUERY_KEY, venue.id])
    } catch {
      snackBar.error('Une erreur est survenue. Merci de réessayer plus tard.')
    } finally {
      setIsModalOpen(false)
      setIsLoading(false)

      selectSoftwareButtonRef.current?.focus()
    }
  }

  return (
    <DeleteVenueProviderDialog
      onConfirm={tryToDeleteVenueProvider}
      onCancel={() => setIsModalOpen(false)}
      isLoading={isLoading}
      isDialogOpen={isModalOpen}
      trigger={
        <Button
          onClick={() => setIsModalOpen(true)}
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullTrashIcon}
          label="Supprimer"
        />
      }
    />
  )
}
