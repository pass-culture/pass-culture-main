import React, { useState } from 'react'

import useNotification from 'components/hooks/useNotification'
import Icon from 'components/layout/Icon'
import { useModal } from 'hooks/useModal'
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
  const notify = useNotification()
  const { visible, showModal, hideModal } = useModal()
  const [isLoading, setIsLoading] = useState(false)

  const onConfirm = async () => {
    setIsLoading(true)
    onImageDelete().catch(() =>
      notify.error('Une erreur est survenue. Merci de réessayer plus tard.')
    )
    setIsLoading(false)
    hideModal()
  }

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
