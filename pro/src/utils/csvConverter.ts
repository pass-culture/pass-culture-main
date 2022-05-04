import Papa from 'papaparse'
const CSV_SEMI_COLON_SEPARATOR = ';'

interface ObjectFromCsv {
  headers: string[]
  data: string[][]
}

const convertFromCsvToObject = (csv: string): ObjectFromCsv => {
  const result: any = Papa.parse(csv, {
    delimiter: CSV_SEMI_COLON_SEPARATOR,
    skipEmptyLines: true,
    dynamicTyping: true,
  })
  const resultData = result.data
  const headers = resultData.shift()
  return {
    headers,
    data: result.data,
  }
}

export default convertFromCsvToObject
