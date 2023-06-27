import React, { useState } from 'react'

import { useModal } from 'hooks/useModal'
import TrashFilledIcon from 'icons/ico-trash-filled.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './ButtonImageDelete.module.scss'
import { ModalImageDelete } from './ModalImageDelete'

export interface IButtonImageDeleteProps {
  onImageDelete: () => Promise<void>
}

const ButtonImageDelete = ({
  onImageDelete,
}: IButtonImageDeleteProps): JSX.Element => {
  const { visible, showModal, hideModal } = useModal()
  const [isLoading, setIsLoading] = useState(false)

  const onConfirm = async () => {
    setIsLoading(true)
    await onImageDelete()
  }

  return (
    <>
      <Button onClick={showModal} variant={ButtonVariant.TERNARY}>
        <TrashFilledIcon className={styles['button-image-delete-icon']} />
        Supprimer
      </Button>
      {!!visible && (
        <ModalImageDelete
          isLoading={isLoading}
          onConfirm={onConfirm}
          onDismiss={hideModal}
        />
      )}
    </>
  )
}

export default ButtonImageDelete
