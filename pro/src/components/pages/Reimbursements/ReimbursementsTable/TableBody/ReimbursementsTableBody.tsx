import React from 'react'

import { Invoice } from 'custom_types'
import { ReactComponent as DownloadSvg } from 'icons/ico-download.svg'

import styles from './ReimbursementsTableBody.module.scss'

interface ITableBody {
  invoices: Invoice[]
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
            <td>{invoice.reference}</td>
            <td className={styles['amount']}>{invoice.amount}€</td>
            <td className={styles['invoice']}>
              <a
                className="bi-link tertiary-link"
                download
                href={invoice.url}
                rel="noopener noreferrer"
                target="_blank"
              >
                <DownloadSvg />
                Télécharger le PDF
              </a>
            </td>
          </tr>
        )
      })}
    </tbody>
  )
}

export default ReimbursementsTableBody
