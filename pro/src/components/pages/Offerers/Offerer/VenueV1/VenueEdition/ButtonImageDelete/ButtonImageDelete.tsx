import React from 'react'

import Icon from 'components/layout/Icon'
import { useModal } from 'hooks/useModal'
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
          isLoading={false}
          onDeleteImage={() => {
            window.alert('Cette fonctionnalité sera développée par PC-13132')
          }}
          onDismiss={hideModal}
        />
      )}
    </>
  )
}
