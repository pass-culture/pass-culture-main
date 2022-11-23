import React from 'react'

import DialogBox from 'components/DialogBox/DialogBox'
import { ReactComponent as AlertSvg } from 'icons/ico-alert-grey.svg'

import styles from './Dialog.module.scss'

export interface IDialogProps {
  onCancel: () => void
  title: string
  secondTitle?: string
  explanation?: React.ReactNode | React.ReactNode[]
  children?: React.ReactNode | React.ReactNode[]
  icon?: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
  hideIcon?: boolean
  extraClassNames?: string
}

const Dialog = ({
  onCancel,
  title,
  secondTitle,
  explanation,
  children,
  icon,
  hideIcon = false,
  extraClassNames,
}: IDialogProps): JSX.Element => {
  const Icon = icon ?? AlertSvg

  return (
    <DialogBox
      extraClassNames={`${styles['dialog']} ${extraClassNames}`}
      hasCloseButton
      labelledBy={title}
      onDismiss={onCancel}
    >
      {!hideIcon && <Icon className={styles['dialog-icon']} />}
      <div className={styles['dialog-title']}>
        {title}
        <span>{secondTitle}</span>
      </div>
      {explanation && (
        <div className={styles['dialog-explanation']}>{explanation}</div>
      )}
      {children}
    </DialogBox>
  )
}

export default Dialog
