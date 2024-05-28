/* istanbul ignore file: DEBT, TO FIX */
import { TableData } from 'screens/CsvTable/types'
import { convertFromCsvToObject } from 'utils/csvConverter'

export const getCsvData = (csvUrl: string): Promise<TableData | null> => {
  return new Promise((resolve, reject) => {
    // eslint-disable-next-line @typescript-eslint/no-extra-semi
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
      } catch (error) {
        reject(null)
      }
    })()
  })
}
