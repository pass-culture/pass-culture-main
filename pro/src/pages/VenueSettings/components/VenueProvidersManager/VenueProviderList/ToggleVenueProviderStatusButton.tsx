import { useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import type {
  GetVenueResponseModel,
  VenueProviderResponse,
} from '@/apiClient/v1'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullPauseIcon from '@/icons/full-pause.svg'
import fullPlayIcon from '@/icons/full-play.svg'

import { ToggleVenueProviderStatusDialog } from './ToggleVenueProviderStatusDialog'

interface ToggleVenueProviderStatusButtonProps {
  venueProvider: VenueProviderResponse
  venue: GetVenueResponseModel
}

export const ToggleVenueProviderStatusButton = ({
  venueProvider,
  venue,
}: ToggleVenueProviderStatusButtonProps) => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const snackBar = useSnackBar()
  const { mutate } = useSWRConfig()

  const updateVenueProviderStatus = async () => {
    setIsLoading(true)
    const payload = {
      ...venueProvider,
      providerId: venueProvider.provider.id,
      isActive: !venueProvider.isActive,
    }

    try {
      await api.updateVenueProvider(venue.id, payload)
      await mutate([GET_VENUE_PROVIDERS_QUERY_KEY, venue.id])
    } catch {
      snackBar.error('Une erreur est survenue. Merci de réessayer plus tard')
    } finally {
      setIsModalOpen(false)
      setIsLoading(false)
    }
  }

  return (
    <ToggleVenueProviderStatusDialog
      onCancel={() => setIsModalOpen(false)}
      onConfirm={updateVenueProviderStatus}
      isLoading={isLoading}
      isActive={venueProvider.isActive}
      isDialogOpen={isModalOpen}
      trigger={
        venueProvider.isActive ? (
          <Button
            onClick={() => setIsModalOpen(true)}
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            icon={fullPauseIcon}
            iconAlt="Mettre en pause la synchronisation"
            label="Mettre en pause"
          />
        ) : (
          <Button
            onClick={() => setIsModalOpen(true)}
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            icon={fullPlayIcon}
            iconAlt="Réactiver la synchronisation"
            label="Réactiver"
          />
        )
      }
    />
  )
}
