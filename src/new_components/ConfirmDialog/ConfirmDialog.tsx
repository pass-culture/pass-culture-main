import React, { useRef } from 'react'

import { ReactComponent as AlertSvg } from "icons/ico-alert-grey.svg"
import DialogBox  from "new_components/DialogBox/DialogBox"

import styles from './ConfirmDialog.module.scss'

interface IConfirmDialogProps {
  onConfirm: () => void;
  onCancel: () => void;
  title: string;
  confirmText: string;
  cancelText: string;
  children: React.ReactNode | React.ReactNode[];
}

const ConfirmDialog = ({
  onConfirm,
  onCancel,
  title,
  confirmText,
  cancelText,
  children  }: IConfirmDialogProps): JSX.Element => {
  const buttonRef = useRef<HTMLButtonElement| null>(null)
  
  return (
    <DialogBox
      extraClassNames={styles["confirm-dialog"]}
      hasCloseButton={false}
      initialFocusRef={buttonRef}
      labelledBy=""
    >
      <AlertSvg />
      <div className={styles["confirm-dialog-title"]}>
        <strong>
          {title}
        </strong>
      </div>
      <div className={styles["confirm-dialog-explanation"]}>
        {children}
      </div>
      <div className={styles["confirm-dialog-actions"]}>
        <button
          className="secondary-button"
          onClick={onCancel}
          type="submit"
        >
          {cancelText}
        </button>
        <button
          className="primary-button"
          onClick={onConfirm}
          ref={buttonRef}
          type="button"
        >
          {confirmText}
        </button>
      </div>
    </DialogBox>
  )
}

export default ConfirmDialog
