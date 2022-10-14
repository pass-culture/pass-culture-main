import React, { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import Icon from 'components/layout/Icon'
import { useModal } from 'hooks/useModal'
import useNotification from 'hooks/useNotification'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { IVenueProviderApi } from '../../VenueProvidersManager/CinemaProviderItem/types'
import ToggleVenueProviderStatusDialog from '../ToggleVenueProviderStatusDialog/ToggleVenueProviderStatusDialog'
import style from '../VenueProviderItemV2/VenueProviderItemV2.module.scss'

export interface IToggleVenueProviderStatusButtonProps {
  venueProvider: IVenueProviderApi
  afterEdit: (venueProvider: IVenueProviderApi) => void
}

const ToggleVenueProviderStatusButton = ({
  venueProvider,
  afterEdit,
}: IToggleVenueProviderStatusButtonProps) => {
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
        // @ts-expect-error string | undefined is not assignable to string | null
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
          <Icon
            alt="Mettre en pause la synchronisation"
            className={style['provider-action-icon']}
            svg="ico-action-pause"
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
