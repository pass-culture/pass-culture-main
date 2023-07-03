import React, { useCallback, useState } from 'react'

import { api } from 'apiClient/api'
import useNotification from 'hooks/useNotification'
import fullTrashIcon from 'icons/full-trash.svg'
import { ButtonVariant } from 'ui-kit/Button/types'
import { Button } from 'ui-kit/index'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import DeleteVenueProviderDialog from '../DeleteVenueProviderDialog/DeleteVenueProviderDialog'
import style from '../VenueProviderItem/VenueProviderItem.module.scss'

interface DeleteVenueProviderButtonProps {
  venueProviderId: number
  afterDelete: (deletedVenueProvider: number) => void
}

const DeleteVenueProviderButton = ({
  venueProviderId,
  afterDelete,
}: DeleteVenueProviderButtonProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const notification = useNotification()

  const tryToDeleteVenueProvider = useCallback(async () => {
    setIsLoading(true)
    try {
      await api.deleteVenueProvider(venueProviderId)

      afterDelete(venueProviderId)
    } catch (exception) {
      notification.error(
        'Une erreur est survenue. Merci de réessayer plus tard.'
      )
    } finally {
      setIsModalOpen(false)
      setIsLoading(false)
    }
  }, [notification])

  return (
    <>
      <Button
        className={style['provider-action-button']}
        onClick={() => setIsModalOpen(true)}
        variant={ButtonVariant.TERNARY}
      >
        <SvgIcon
          src={fullTrashIcon}
          alt=""
          className={style['provider-action-icon']}
        />
        Supprimer
      </Button>

      {isModalOpen && (
        <DeleteVenueProviderDialog
          onConfirm={tryToDeleteVenueProvider}
          onCancel={() => setIsModalOpen(false)}
          isLoading={isLoading}
        />
      )}
    </>
  )
}

export default DeleteVenueProviderButton
