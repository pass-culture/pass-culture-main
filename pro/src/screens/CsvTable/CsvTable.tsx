import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { Spinner } from 'ui-kit/Spinner/Spinner'
import { API_URL } from 'utils/config'
import { getKey } from 'utils/strings'

import styles from './CsvTable.module.scss'
import { TableData } from './types'

export interface CsvTableProps {
  getCsvData: (url: string) => Promise<TableData | null>
}

export const CsvTableScreen = ({ getCsvData }: CsvTableProps): JSX.Element => {
  const { search } = useLocation()
  const [dataFromCsv, setDataFromCsv] = useState<TableData | null>()
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const loadData = async () => {
      const searchParams = new URLSearchParams(search)

      try {
        const response = await getCsvData(
          `${API_URL}/reimbursements/csv?${searchParams}`
        )
        setDataFromCsv(response)
      } catch {
        setDataFromCsv(null)
      } finally {
        setIsLoading(false)
      }
    }

    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadData()
  }, [getCsvData, search])

  return isLoading ? (
    <div className={styles['spinner-container']}>
      <Spinner />
    </div>
  ) : dataFromCsv?.data.length ? (
    <main className={styles['csv-main-container']}>
      <div className={styles['csv-container']}>
        <table className={styles['csv-table']}>
          <thead>
            <tr>
              {dataFromCsv.headers.map((header) => (
                <th key={getKey(`header_${header}`)}>{header}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {dataFromCsv.data.map((line, indexLine) => (
              <tr key={getKey(`line_${indexLine}`)}>
                {line.map((content, indexContent) => (
                  <td
                    key={getKey(`line__${indexLine}_content_${indexContent}`)}
                  >
                    {content}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <hr />
    </main>
  ) : (
    <main className={styles['no-data-container']}>
      <p>Il n’y a pas de données à afficher.</p>
    </main>
  )
}
