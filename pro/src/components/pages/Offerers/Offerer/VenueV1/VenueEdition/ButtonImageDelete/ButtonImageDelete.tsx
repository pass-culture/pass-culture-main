import React, { useCallback, useState } from 'react'

import useNotification from 'components/hooks/useNotification'
import Icon from 'components/layout/Icon'
import { useModal } from 'hooks/useModal'
import { deleteVenueImage } from 'repository/pcapi/pcapi'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './ButtonImageDelete.module.scss'
import { VenueImageDeleteModal } from './VenueImageDeleteModal'

type ButtonImageDeleteProps = {
  venueId: string
  onDeleteImage: () => void
}

export const ButtonImageDelete = ({
  venueId,
  onDeleteImage,
}: ButtonImageDeleteProps): JSX.Element => {
  const { visible, showModal, hideModal } = useModal()
  const [isLoading, setIsLoading] = useState(false)
  const notification = useNotification()

  const tryToDeleteVenueImage = useCallback(async () => {
    setIsLoading(true)
    try {
      await deleteVenueImage({ venueId })

      onDeleteImage()
    } catch (exception) {
      notification.error(
        'Une erreur est survenue. Merci de réessayer plus tard.'
      )
    } finally {
      hideModal()
      setIsLoading(false)
    }
  }, [notification, onDeleteImage, hideModal, venueId])

  return (
    <>
      <Button onClick={showModal} variant={ButtonVariant.TERNARY}>
        <Icon
          className={styles['button-image-delete-icon']}
          svg="ico-trash-filled"
        />
        Supprimer
      </Button>

      {!!visible && (
        <VenueImageDeleteModal
          isLoading={isLoading}
          onDeleteImage={tryToDeleteVenueImage}
          onDismiss={hideModal}
        />
      )}
    </>
  )
}
