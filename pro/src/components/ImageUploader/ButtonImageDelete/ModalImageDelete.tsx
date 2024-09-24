import React from 'react'
import { useTranslation } from 'react-i18next'

import { ConfirmDialog } from 'components/Dialog/ConfirmDialog/ConfirmDialog'
import strokeTrashIcon from 'icons/stroke-trash.svg'

interface ModalImageDeleteProps {
  isLoading: boolean
  onConfirm: () => void
  onDismiss: () => void
}

export const ModalImageDelete = ({
  isLoading,
  onConfirm,
  onDismiss,
}: ModalImageDeleteProps): JSX.Element => {
  const { t } = useTranslation('common')
  return (
    <ConfirmDialog
      cancelText={t('back')}
      confirmText="Supprimer"
      icon={strokeTrashIcon}
      isLoading={isLoading}
      onCancel={onDismiss}
      onConfirm={onConfirm}
      title="Supprimer l’image"
    >
      Souhaitez-vous vraiment supprimer cette image ?
    </ConfirmDialog>
  )
}
