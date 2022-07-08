import { ReactComponent as InfoIcon } from 'icons/info.svg'
import React from 'react'
import { Title } from 'ui-kit'
import styles from './LeavingGuardDialog.module.scss'

interface LeavingGuardDialogProps {
  title: string
  message: string
}

const LeavingGuardDialog = ({
  title,
  message,
}: LeavingGuardDialogProps): JSX.Element => {
  return (
    <div className={styles['dialog']}>
      <InfoIcon className={styles['dialog-icon']} />
      <Title level={3}>{title}</Title>
      <p>{message}</p>
    </div>
  )
}

export default LeavingGuardDialog
