import React, { useCallback, useEffect, useRef, useState } from 'react'

import useNotification from 'components/hooks/useNotification'
import { useModal } from 'hooks/useModal'
import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import { deleteVenueProvider } from 'repository/pcapi/pcapi'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import DeleteVenueProviderDialog from '../DeleteVenueProviderDialog/DeleteVenueProviderDialog'
import style from '../VenueProviderItemV2/VenueProviderItemV2.module.scss'

export interface IDeleteVenueProviderButtonProps {
  venueProviderId: string
  afterDelete: (deletedVenueProvider: string) => void
}

const DeleteVenueProviderButton = ({
  venueProviderId,
  afterDelete,
}: IDeleteVenueProviderButtonProps): JSX.Element => {
  const { visible, showModal, hideModal } = useModal()
  const [isLoading, setIsLoading] = useState(false)
  const notification = useNotification()
  const mountedRef = useRef(true)

  useEffect(() => {
    return () => {
      mountedRef.current = false
    }
  }, [])

  const tryToDeleteVenueProvider = useCallback(async () => {
    setIsLoading(true)
    try {
      await deleteVenueProvider(venueProviderId)

      afterDelete(venueProviderId)
    } catch (exception) {
      notification.error(
        'Une erreur est survenue. Merci de réessayer plus tard.'
      )
    } finally {
      if (mountedRef.current) {
        hideModal()
        setIsLoading(false)
      }
    }
  }, [notification, hideModal])
  return (
    <>
      <Button
        className={style['provider-action-button']}
        onClick={showModal}
        variant={ButtonVariant.TERNARY}
      >
        <TrashFilledIcon
          title="Supprimer la synchronisation"
          className={style['provider-action-icon']}
        />
        Supprimer
      </Button>
      {visible && (
        <DeleteVenueProviderDialog
          onConfirm={tryToDeleteVenueProvider}
          onCancel={hideModal}
          isLoading={isLoading}
        />
      )}
    </>
  )
}

export default DeleteVenueProviderButton
