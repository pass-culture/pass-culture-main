import React, { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import { VenueProviderResponse } from 'apiClient/v1'
import useNotification from 'hooks/useNotification'
import fullPauseIcon from 'icons/full-pause.svg'
import fullPlayIcon from 'icons/full-play.svg'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Button } from 'ui-kit/index'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { ToggleVenueProviderStatusDialog } from './ToggleVenueProviderStatusDialog'
import style from './VenueProviderItem.module.scss'

interface ToggleVenueProviderStatusButtonProps {
  venueProvider: VenueProviderResponse
  afterEdit: (venueProvider: VenueProviderResponse) => void
}

export const ToggleVenueProviderStatusButton = ({
  venueProvider,
  afterEdit,
}: ToggleVenueProviderStatusButtonProps) => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const notification = useNotification()

  const updateVenueProviderStatus = useCallback(async () => {
    setIsLoading(true)
    const payload = {
      ...venueProvider,
      providerId: venueProvider.provider.id,
      isActive: !venueProvider.isActive,
    }

    try {
      const editedVenueProvider = await api.updateVenueProvider(payload)
      afterEdit(editedVenueProvider)
    } catch {
      notification.error(
        'Une erreur est survenue. Merci de réessayer plus tard'
      )
    } finally {
      setIsModalOpen(false)
      setIsLoading(false)
    }
  }, [notification, venueProvider])

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
