const MAX_FILE_SIZE = 1048576
const CARRIAGE_RETURN = '\n'
const UNAUTHORIZED_CHARACTERS = /[,;.]/
const MAX_CODE_DISPLAY = 5

export const csvToRows = (str = '') => {
  if ((str || '').indexOf(CARRIAGE_RETURN) === -1) {
    return []
  }
  const rowsAsString = str.split(CARRIAGE_RETURN)
  return rowsAsString.map(row => row.trim()).filter(row => row.length)
}

export const fileReader = file => {
  const reader = new FileReader()

  return new Promise(resolve => {
    reader.onerror = () => {
      reader.abort()
      resolve(null)
    }

    reader.onload = () => {
      resolve(reader.result)
    }
    reader.readAsText(file)
  })
}

export const checkAndParseUploadedFile = async ({
  fileReader,
  currentFile,
}) => {
  if (currentFile.size > MAX_FILE_SIZE) {
    return { errorMessage: 'Le poids du fichier ne doit pas dépasser 1 Mo.' }
  }

  const fileContent = await fileReader(currentFile)
  if (!fileContent) {
    return {
      errorMessage:
        'Le fichier est vide ou illisible, veuillez réessayer ou contacter le support.',
    }
  }

  const rows = csvToRows(fileContent)

  if (!rows.length) {
    return { errorMessage: 'Le fichier ne contient aucun code d’activation.' }
  }

  if (rows.some(row => row.match(UNAUTHORIZED_CHARACTERS))) {
    return {
      errorMessage:
        'Le fichier ne respecte pas le format attendu. Merci de vous rapporter au gabarit CSV disponible au téléchargement.',
    }
  }

  if ([...new Set(rows)].length < rows.length) {
    const countByCode = rows.reduce((acc, cur) => {
      if (!acc[cur]) {
        acc[cur] = 1
      } else {
        acc[cur] = ++acc[cur]
      }
      return acc
    }, {})
    const codeNonUniques = [
      ...new Set(rows.filter(code => countByCode[code] > 1)),
    ]
    return {
      errorMessage: `Plusieurs codes identiques ont été trouvés dans le fichier : ${codeNonUniques
        .slice(0, MAX_CODE_DISPLAY)
        .join(', ')}${MAX_CODE_DISPLAY < codeNonUniques.length ? '... ' : ''}.`,
    }
  }

  return { activationCodes: rows }
}
