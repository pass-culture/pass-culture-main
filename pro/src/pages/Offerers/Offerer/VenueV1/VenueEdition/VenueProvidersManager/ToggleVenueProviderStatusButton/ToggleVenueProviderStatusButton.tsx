import React, { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import { VenueProviderResponse } from 'apiClient/v1'
import { useModal } from 'hooks/useModal'
import useNotification from 'hooks/useNotification'
import fullPauseIcon from 'icons/full-pause.svg'
import { ButtonVariant } from 'ui-kit/Button/types'
import Icon from 'ui-kit/Icon/Icon'
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
  const { visible, showModal, hideModal } = useModal()
  const [isLoading, setIsLoading] = useState(false)
  const notification = useNotification()

  const updateVenueProviderStatus = useCallback(async () => {
    setIsLoading(true)
    const payload = {
      ...venueProvider,
      isActive: !venueProvider.isActive,
    }
    api
      // @ts-expect-error boolean | null is not assignable to boolean | undefined
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
        hideModal()
        setIsLoading(false)
      })
  }, [notification, hideModal, venueProvider])

  return (
    <>
      {venueProvider.isActive ? (
        <Button
          className={style['provider-action-button']}
          onClick={showModal}
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
          onClick={showModal}
          variant={ButtonVariant.TERNARY}
        >
          <Icon
            alt="Réactiver la synchronisation"
            className={style['provider-action-icon']}
            svg="ico-action-play"
          />
          Réactiver
        </Button>
      )}
      {visible && (
        <ToggleVenueProviderStatusDialog
          onCancel={hideModal}
          onConfirm={updateVenueProviderStatus}
          isLoading={isLoading}
          isActive={venueProvider.isActive}
        />
      )}
    </>
  )
}

export default ToggleVenueProviderStatusButton
