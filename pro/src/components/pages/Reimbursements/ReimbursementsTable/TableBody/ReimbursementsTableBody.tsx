import React from 'react'

import { InvoiceResponseModel } from 'apiClient/v1'
import { ReactComponent as DownloadSvg } from 'icons/ico-download.svg'

import styles from './ReimbursementsTableBody.module.scss'

interface ITableBody {
  invoices: InvoiceResponseModel[]
}

const ReimbursementsTableBody = ({ invoices }: ITableBody): JSX.Element => {
  return (
    <tbody className={styles['reimbursement-body']}>
      {invoices.map(invoice => {
        return (
          <tr key={invoice.reference}>
            <td className={styles['date']}>{invoice.date}</td>
            <td className={styles['business-unit']}>
              {invoice.businessUnitName}
            </td>
            <td className={styles['reference']}>{invoice.reference}</td>
            {/* For now only one label is possible by invoice. */}
            <td className={styles['label']}>{invoice.cashflowLabels[0]}</td>
            <td className={styles['amount']}>{invoice.amount}&nbsp;€</td>
            <td className={styles['invoice']}>
              <a
                className="bi-link tertiary-link"
                download
                href={invoice.url}
                rel="noopener noreferrer"
                target="_blank"
                aria-label="Télécharger le PDF"
              >
                <DownloadSvg />
                PDF
              </a>
            </td>
          </tr>
        )
      })}
    </tbody>
  )
}

export default ReimbursementsTableBody
