import React from 'react'

import strokeRepaymentIcon from 'icons/stroke-repayment.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './InvoicesNoResult.module.scss'

export const NoInvoicesYet = (): JSX.Element => {
  return (
    <div className={styles['no-refunds']}>
      <SvgIcon
        src={strokeRepaymentIcon}
        alt=""
        width="100"
        className={styles['no-refunds-icon']}
      />
      <p className={styles['no-refunds-title']}>
        Vous n’avez pas encore de justificatifs de remboursement disponibles
      </p>
      <p>Lorsqu’ils auront été édités, vous pourrez les télécharger ici</p>
    </div>
  )
}
