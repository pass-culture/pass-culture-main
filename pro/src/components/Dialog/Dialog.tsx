import * as RadixDialog from '@radix-ui/react-dialog'
import type React from 'react'
import { type JSX, useId } from 'react'

import strokeErrorIcon from '@/icons/stroke-error.svg'
import {
  DialogBuilder,
  type DialogBuilderProps,
} from '@/ui-kit/DialogBuilder/DialogBuilder'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './Dialog.module.scss'

export interface DialogProps {
  onCancel: () => void
  onClose?: () => void
  title: string
  secondTitle?: string
  explanation?: React.ReactNode | React.ReactNode[]
  children?: React.ReactNode | React.ReactNode[]
  icon?: string
  hideIcon?: boolean
  extraClassNames?: string
  trigger?: React.ReactNode | React.ReactNode[]
  refToFocusOnClose?: DialogBuilderProps['refToFocusOnClose']
  // TODO (igabriele, 2025-08-18): We should rely on conditonally rendering rather than an open prop (perf, top-down decision tree).
  open: boolean
}

export const Dialog = ({
  onCancel,
  onClose,
  title,
  secondTitle,
  explanation,
  children,
  icon,
  hideIcon = false,
  extraClassNames,
  trigger,
  open,
  refToFocusOnClose,
}: DialogProps): JSX.Element => {
  const titleId = useId()

  return (
    <DialogBuilder
      open={open}
      onOpenChange={(open) => !open && (onClose ? onClose() : onCancel())}
      trigger={trigger}
      refToFocusOnClose={refToFocusOnClose}
    >
      <div className={`${styles['dialog']} ${extraClassNames}`}>
        {!hideIcon && (
          <SvgIcon
            src={icon ?? strokeErrorIcon}
            alt=""
            className={styles['dialog-icon']}
          />
        )}
        <RadixDialog.Title>
          <div className={styles['dialog-title']} id={titleId}>
            {title}
            <span>{secondTitle}</span>
          </div>
        </RadixDialog.Title>
        {explanation && (
          <div className={styles['dialog-explanation']}>{explanation}</div>
        )}
        {children}
      </div>
    </DialogBuilder>
  )
}
