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
  dangerouslyBypassFocusLock?: boolean
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
  dangerouslyBypassFocusLock,
}: DialogProps): JSX.Element => {
  const titleId = useId()

  return (
    <DialogBox
      extraClassNames={`${styles['dialog']} ${extraClassNames}`}
      hasCloseButton
      labelledBy={titleId}
      onDismiss={onCancel}
      dangerouslyBypassFocusLock={dangerouslyBypassFocusLock}
    >
      {!hideIcon && (
        <SvgIcon
          src={icon ?? strokeErrorIcon}
          alt=""
          className={styles['dialog-icon']}
        />
      )}
      <h1 className={styles['dialog-title']} id={titleId}>
        {title}
        <span>{secondTitle}</span>
      </h1>
      {explanation && (
        <div className={styles['dialog-explanation']}>{explanation}</div>
      )}
      {children}
    </DialogBox>
  )
}

export default Dialog
