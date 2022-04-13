import { parse } from 'csv-parse/lib/sync'
const CSV_SEMI_COLON_SEPARATOR = ';'

interface ObjectFromCsv {
  headers: string[]
  data: string[][]
}

const convertFromCsvToObject = (csv: string): ObjectFromCsv => {
  const rows = parse(csv, {
    delimiter: CSV_SEMI_COLON_SEPARATOR,
    skip_empty_lines: true,
  })

  const headers = rows.shift()
  return {
    headers,
    data: rows,
  }
}

export default convertFromCsvToObject
