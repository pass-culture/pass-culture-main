import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import type { ITableData } from 'screens/CsvTable'
import Spinner from 'ui-kit/Spinner/Spinner'
import { API_URL } from 'utils/config'
import { getKey } from 'utils/strings'

export interface ICsvTableProps {
  getCsvData: (url: string) => Promise<ITableData | null>
}

const CsvTable = ({ getCsvData }: ICsvTableProps): JSX.Element => {
  const { search } = useLocation()
  const [dataFromCsv, setDataFromCsv] = useState<ITableData | null>()
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const searchParams = new URLSearchParams(search)

    getCsvData(`${API_URL}/reimbursements/csv?${searchParams}`)
      .then((res: ITableData | null) => {
        setDataFromCsv(res)
      })
      .catch(() => {
        setDataFromCsv(null)
      })
      .finally(() => setIsLoading(false))
  }, [getCsvData, search])

  return isLoading ? (
    <div id="spinner-container">
      <Spinner />
    </div>
  ) : dataFromCsv?.data?.length ? (
    <main id="content" className="csv-main-container">
      <div id="csv-container">
        <table id="csv-table">
          <thead>
            <tr>
              {dataFromCsv.headers.map(header => (
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
    <main id="content" className="no-data-container">
      <p>Il n’y a pas de données à afficher.</p>
    </main>
  )
}

export default CsvTable
