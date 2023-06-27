import React from 'react'

import DialogBox from 'components/DialogBox'
import Icon from 'ui-kit/Icon/Icon'

import styles from './InfoDialog.module.scss'

interface InfoDialogProps {
  buttonText: string
  iconName?: string
  title: string
  subTitle: string
  componentIcon?: React.ReactElement
  closeDialog: () => void
}

const InfoDialog = ({
  buttonText,
  iconName,
  title,
  subTitle,
  componentIcon,
  closeDialog,
}: InfoDialogProps): JSX.Element => {
  return (
    <DialogBox
      hasCloseButton
      labelledBy={title}
      onDismiss={closeDialog}
      extraClassNames={styles['info-dialog']}
    >
      {!!iconName && (
        <Icon className={styles['info-dialog-icon']} svg={iconName} />
      )}
      {componentIcon && (
        <div className={styles['info-dialog-icon-component']}>
          {componentIcon}
        </div>
      )}
      <div className={styles['info-dialog-title']}>
        <strong>{title}</strong>
      </div>
      <div className={styles['info-dialog-subtitle']}>{subTitle}</div>
      <div className={styles['info-dialog-actions']}>
        <button className="primary-button" onClick={closeDialog} type="button">
          {buttonText}
        </button>
      </div>
    </DialogBox>
  )
}

export default InfoDialog
