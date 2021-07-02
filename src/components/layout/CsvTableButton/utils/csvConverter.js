const CSV_SEMI_COLON_SEPARATOR = ';'
const parse = require('csv-parse/lib/sync')

const convertFromCsvToObject = csv => {
  const rows = parse(csv, {
    delimiter: CSV_SEMI_COLON_SEPARATOR,
    skip_empty_lines: true,
    cast: value => {
      if (value && !Number.isNaN(Number(value))) {
        return value.replace('.', ',')
      }
      return value
    },
  })

  const headers = rows.shift()
  return {
    headers,
    data: rows,
  }
}

export default convertFromCsvToObject
