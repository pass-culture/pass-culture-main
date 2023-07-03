import React, { useId } from 'react'

import DialogBox from 'components/DialogBox/DialogBox'
import strokeErrorIcon from 'icons/stroke-error.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './Dialog.module.scss'

export interface DialogProps {
  onCancel: () => void
  title: string
  secondTitle?: string
  explanation?: React.ReactNode | React.ReactNode[]
  children?: React.ReactNode | React.ReactNode[]
  icon?: string
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
}: DialogProps): JSX.Element => {
  const titleId = useId()

  return (
    <DialogBox
      extraClassNames={`${styles['dialog']} ${extraClassNames}`}
      hasCloseButton
      labelledBy={titleId}
      onDismiss={onCancel}
    >
      {!hideIcon && (
        <SvgIcon
          src={icon ?? strokeErrorIcon}
          alt=""
          className={styles['dialog-icon']}
        />
      )}
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
