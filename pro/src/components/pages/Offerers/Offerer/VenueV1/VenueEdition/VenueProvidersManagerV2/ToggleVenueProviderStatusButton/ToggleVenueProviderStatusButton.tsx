import * as pcapi from 'repository/pcapi/pcapi'
import React, { useCallback, useState } from 'react'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'
import { IVenueProviderApi } from '../../VenueProvidersManager/CinemaProviderItem/types'
import Icon from 'components/layout/Icon'
import ToggleVenueProviderStatusDialog from '../ToggleVenueProviderStatusDialog/ToggleVenueProviderStatusDialog'
import style from '../VenueProviderItemV2/VenueProviderItemV2.module.scss'
import { useModal } from 'hooks/useModal'
import useNotification from 'components/hooks/useNotification'

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
    pcapi
      .editVenueProvider(payload)
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
        <Button onClick={showModal} variant={ButtonVariant.TERNARY}>
          <Icon
            alt="Mettre en pause la synchronisation"
            className={style['provider-action-icon']}
            svg="ico-action-pause"
          />
          Mettre en pause
        </Button>
      ) : (
        <Button onClick={showModal} variant={ButtonVariant.TERNARY}>
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
