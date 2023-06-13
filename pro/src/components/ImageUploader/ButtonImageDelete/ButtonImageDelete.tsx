import React, { useState } from 'react'

import { ReactComponent as TrashFilledIcon } from 'icons/ico-trash-filled.svg'
import { Button } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import styles from './ButtonImageDelete.module.scss'
import { ModalImageDelete } from './ModalImageDelete'

export interface ButtonImageDeleteProps {
  onImageDelete: () => Promise<void>
}

const ButtonImageDelete = ({
  onImageDelete,
}: ButtonImageDeleteProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const onConfirm = async () => {
    setIsLoading(true)
    await onImageDelete()
  }

  return (
    <>
      <Button
        onClick={() => setIsModalOpen(true)}
        variant={ButtonVariant.TERNARY}
      >
        <TrashFilledIcon className={styles['button-image-delete-icon']} />
        Supprimer
      </Button>

      {isModalOpen && (
        <ModalImageDelete
          isLoading={isLoading}
          onConfirm={onConfirm}
          onDismiss={() => setIsModalOpen(false)}
        />
      )}
    </>
  )
}

export default ButtonImageDelete
