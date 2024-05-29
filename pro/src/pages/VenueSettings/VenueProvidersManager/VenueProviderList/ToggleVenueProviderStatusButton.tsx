import React, { useState } from 'react'
import { useSWRConfig } from 'swr'

import { api } from 'apiClient/api'
import { GetVenueResponseModel, VenueProviderResponse } from 'apiClient/v1'
import { GET_VENUE_PROVIDERS_QUERY_KEY } from 'config/swrQueryKeys'
import { useNotification } from 'hooks/useNotification'
import fullPauseIcon from 'icons/full-pause.svg'
import fullPlayIcon from 'icons/full-play.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { ToggleVenueProviderStatusDialog } from './ToggleVenueProviderStatusDialog'
import style from './VenueProviderItem.module.scss'

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
      {venueProvider.isActive ? (
        <Button
          onClick={() => setIsModalOpen(true)}
          variant={ButtonVariant.TERNARY}
        >
          <SvgIcon
            src={fullPauseIcon}
            alt="Mettre en pause la synchronisation"
            className={style['provider-action-icon']}
          />
          Mettre en pause
        </Button>
      ) : (
        <Button
          onClick={() => setIsModalOpen(true)}
          variant={ButtonVariant.TERNARY}
        >
          <SvgIcon
            src={fullPlayIcon}
            alt="Réactiver la synchronisation"
            className={style['provider-action-icon']}
          />
          Réactiver
        </Button>
      )}

      {isModalOpen && (
        <ToggleVenueProviderStatusDialog
          onCancel={() => setIsModalOpen(false)}
          onConfirm={updateVenueProviderStatus}
          isLoading={isLoading}
          isActive={venueProvider.isActive}
        />
      )}
    </>
  )
}
