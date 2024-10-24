/* istanbul ignore file: DEBT, TO FIX */
import { convertFromCsvToObject } from 'commons/utils/csvConverter'
import { TableData } from 'pages/CsvTable/components/CsvTable/types'

export const getCsvData = (csvUrl: string): Promise<TableData | null> => {
  return new Promise((resolve, reject) => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    ;(async () => {
      try {
        const result = await fetch(csvUrl, { credentials: 'include' })
        const { status } = result
        if (status === 200) {
          const text = await result.text()
          resolve(convertFromCsvToObject(text))
        } else {
          reject(null)
        }
      } catch {
        reject(null)
      }
    })()
  })
}
