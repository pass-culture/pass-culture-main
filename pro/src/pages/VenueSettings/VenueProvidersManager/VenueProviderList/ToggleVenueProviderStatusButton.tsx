import { useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from '@/apiClient/api'
import { GetVenueResponseModel, VenueProviderResponse } from '@/apiClient/v1'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from '@/commons/config/swrQueryKeys'
import { useNotification } from '@/commons/hooks/useNotification'
import fullPauseIcon from '@/icons/full-pause.svg'
import fullPlayIcon from '@/icons/full-play.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

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
  const notification = useNotification()
  const { mutate } = useSWRConfig()

  const updateVenueProviderStatus = async () => {
    setIsLoading(true)
    const payload = {
      ...venueProvider,
      providerId: venueProvider.provider.id,
      isActive: !venueProvider.isActive,
    }

    try {
      await api.updateVenueProvider(payload)
      await mutate([GET_VENUE_PROVIDERS_QUERY_KEY, venue.id])
    } catch {
      notification.error(
        'Une erreur est survenue. Merci de réessayer plus tard'
      )
    } finally {
      setIsModalOpen(false)
      setIsLoading(false)
    }
  }

  return (
    <>
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
              variant={ButtonVariant.TERNARY}
              icon={fullPauseIcon}
              iconAlt="Mettre en pause la synchronisation"
            >
              Mettre en pause
            </Button>
          ) : (
            <Button
              onClick={() => setIsModalOpen(true)}
              variant={ButtonVariant.TERNARY}
              icon={fullPlayIcon}
              iconAlt="Réactiver la synchronisation"
            >
              Réactiver
            </Button>
          )
        }
      />
    </>
  )
}
