import { useState } from 'react'

import fullTrashIcon from '@/icons/full-trash.svg'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './ButtonImageDelete.module.scss'
import { ModalImageDelete } from './ModalImageDelete'

export interface ButtonImageDeleteProps {
  onImageDelete: () => void
}

export const ButtonImageDelete = ({
  onImageDelete,
}: ButtonImageDeleteProps): JSX.Element => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const onConfirm = () => {
    setIsLoading(true)
    onImageDelete()
  }

  return (
    <ModalImageDelete
      isLoading={isLoading}
      onConfirm={onConfirm}
      onDismiss={() => setIsModalOpen(false)}
      isDialogOpen={isModalOpen}
      trigger={
        <Button
          onClick={() => setIsModalOpen(true)}
          variant={ButtonVariant.TERNARY}
        >
          <SvgIcon
            alt=""
            className={styles['button-image-delete-icon']}
            src={fullTrashIcon}
          />
          Supprimer
        </Button>
      }
    />
  )
}
