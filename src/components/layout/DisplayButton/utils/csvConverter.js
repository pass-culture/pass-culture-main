const CSV_SEMI_COLON_SEPARATOR = ';'

const convertFromCsvToObject = (csv) => {
  const lines = csv.split('\n')
  const headers = lines[0].split(CSV_SEMI_COLON_SEPARATOR)
  const data = []

  for (let i = 1; i < lines.length; i++) {
    const currentLine = lines[i].split(CSV_SEMI_COLON_SEPARATOR)

    if (currentLine.length > 1) {
      data.push(currentLine)
    }
  }

  return {
    headers,
    data
  }
}

export default convertFromCsvToObject
