import React, { useRef } from 'react'

import Icon from 'components/layout/Icon'
import DialogBox from 'new_components/DialogBox'

import styles from './InfoDialog.module.scss'

interface IInfoDialogProps {
  buttonText: string
  iconName?: string
  title: string
  subTitle: string

  closeDialog: () => void
}

const InfoDialog = ({
  buttonText,
  iconName,
  title,
  subTitle,
  closeDialog,
}: IInfoDialogProps): JSX.Element => {
  const buttonRef = useRef<HTMLButtonElement | null>(null)

  return (
    <DialogBox
      hasCloseButton
      initialFocusRef={buttonRef}
      labelledBy={title}
      onDismiss={closeDialog}
      extraClassNames={styles['info-dialog']}
    >
      {!!iconName && (
        <Icon className={styles['info-dialog-icon']} svg={iconName} />
      )}
      <div className={styles['info-dialog-title']}>
        <strong>{title}</strong>
      </div>
      <div className={styles['info-dialog-subtitle']}>{subTitle}</div>
      <div className={styles['info-dialog-actions']}>
        <button
          className="primary-button"
          onClick={closeDialog}
          type="submit"
          ref={buttonRef}
        >
          {buttonText}
        </button>
      </div>
    </DialogBox>
  )
}

export default InfoDialog
