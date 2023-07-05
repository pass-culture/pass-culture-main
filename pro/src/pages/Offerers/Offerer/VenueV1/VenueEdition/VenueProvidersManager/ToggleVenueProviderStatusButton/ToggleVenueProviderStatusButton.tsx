import React, { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import { VenueProviderResponse } from 'apiClient/v1'
import useNotification from 'hooks/useNotification'
import fullPauseIcon from 'icons/full-pause.svg'
import fullPlayIcon from 'icons/full-play.svg'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Button } from 'ui-kit/index'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import ToggleVenueProviderStatusDialog from '../ToggleVenueProviderStatusDialog/ToggleVenueProviderStatusDialog'
import style from '../VenueProviderItem/VenueProviderItem.module.scss'

interface ToggleVenueProviderStatusButtonProps {
  venueProvider: VenueProviderResponse
  afterEdit: (venueProvider: VenueProviderResponse) => void
}

const ToggleVenueProviderStatusButton = ({
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
      // Price is a number in VenueProviderResponse but PostVenueProviderBody expects a string
      // We should probably fix this at some point
      price: venueProvider.price?.toString(),
      providerId: venueProvider.provider.id,
      isActive: !venueProvider.isActive,
    }
    api
      .updateVenueProvider(payload)
      .then(editedVenueProvider => {
        afterEdit(editedVenueProvider)
      })
      .catch(() => {
        notification.error(
          'Une erreur est survenue. Merci de réessayer plus tard'
        )
      })
      .finally(() => {
        setIsModalOpen(false)
        setIsLoading(false)
      })
  }, [notification, venueProvider])

  return (
    <>
      {venueProvider.isActive ? (
        <Button
          className={style['provider-action-button']}
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
          className={style['provider-action-button']}
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

export default ToggleVenueProviderStatusButton
