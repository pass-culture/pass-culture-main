import React, { FunctionComponent, useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import Spinner from 'components/layout/Spinner'
import type { CsvData } from 'screens/CsvTable'
import { API_URL } from 'utils/config'
import { getKey } from 'utils/strings'

interface Props {
  getCsvData: (url: string) => Promise<CsvData | null>
}

const CsvTable: FunctionComponent<Props> = ({ getCsvData }) => {
  const { search } = useLocation()

  const handlePrintCurrentView = () => window.print()
  const [dataFromCsv, setDataFromCsv] = useState<CsvData | null>()
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    const searchParams = new URLSearchParams(search)

    getCsvData(`${API_URL}/reimbursements/csv?${searchParams}`)
      .then((res: CsvData | null) => {
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
    <main id="main-container">
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
      <div id="csv-print-container">
        <button
          className="button is-primary"
          id="csv-print-button"
          onClick={handlePrintCurrentView}
          type="button"
        >
          Imprimer
        </button>
      </div>
    </main>
  ) : (
    <main className="no-data-container">
      <p>Il n’y a pas de données à afficher.</p>
    </main>
  )
}

export default CsvTable
