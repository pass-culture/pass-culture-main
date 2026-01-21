import { useState } from 'react'

import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullTrashIcon from '@/icons/full-trash.svg'

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
  const snackBar = useSnackBar()

  const onConfirm = () => {
    setIsLoading(true)
    onImageDelete()
    snackBar.success('Votre image a bien été supprimée')
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
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          icon={fullTrashIcon}
          iconClassName={styles['button-image-delete-icon']}
          label="Supprimer"
        />
      }
    />
  )
}
