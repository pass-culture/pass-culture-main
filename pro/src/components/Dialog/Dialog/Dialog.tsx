import React, { useId } from 'react'

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
  const titleId = useId()

  return (
    <DialogBox
      extraClassNames={`${styles['dialog']} ${extraClassNames}`}
      hasCloseButton
      labelledBy={titleId}
      onDismiss={onCancel}
    >
      {!hideIcon && <Icon className={styles['dialog-icon']} />}
      <div className={styles['dialog-title']} id={titleId}>
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
