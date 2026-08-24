const MAX_FILE_SIZE = 1048576
const MAX_FILE_SIZE_TEXT = '1 Mo'
const CARRIAGE_RETURN = '\n'
const UNAUTHORIZED_CHARACTERS = /[,;.]/
const MAX_CODE_DISPLAY = 5

export enum ActivationCodeFileErrorCode {
  NO_FILE = 'NO_FILE',
  FILE_TOO_LARGE = 'FILE_TOO_LARGE',
  FILE_UNREADABLE = 'FILE_UNREADABLE',
  INVALID_FORMAT = 'INVALID_FORMAT',
  DUPLICATED_CODES = 'DUPLICATED_CODES',
}

const csvToRows = (str = '') => {
  if (!(str || '').includes(CARRIAGE_RETURN)) {
    return []
  }
  const rowsAsString = str.split(CARRIAGE_RETURN)
  return rowsAsString.map((row) => row.trim()).filter((row) => row.length)
}

export const fileReader = async (file: Blob) => {
  try {
    return await file.text()
  } catch {
    return null
  }
}

export const checkAndParseUploadedFile = async ({
  fileReader,
  currentFile,
}: {
  fileReader: (file: Blob) => Promise<string | null>
  currentFile: Blob
}) => {
  if (!currentFile) {
    return {
      errorCode: ActivationCodeFileErrorCode.NO_FILE,
      errorMessage: 'Aucun fichier sélectionné.',
    }
  }

  if (currentFile.size > MAX_FILE_SIZE) {
    return {
      errorCode: ActivationCodeFileErrorCode.FILE_TOO_LARGE,
      errorMessage: `Le fichier ne respecte pas le poids attendu. La taille maximale du fichier ne doit pas dépasser ${MAX_FILE_SIZE_TEXT}.`,
    }
  }

  const fileContent = await fileReader(currentFile)
  if (!fileContent) {
    return {
      errorCode: ActivationCodeFileErrorCode.FILE_UNREADABLE,
      errorMessage:
        'Le fichier est vide ou illisible, veuillez réessayer ou contacter le support.',
    }
  }

  const rows = csvToRows(fileContent)

  if (
    !rows.length ||
    rows.some((row) => UNAUTHORIZED_CHARACTERS.exec(row) !== null)
  ) {
    return {
      errorCode: ActivationCodeFileErrorCode.INVALID_FORMAT,
      errorMessage:
        'Le fichier ne respecte pas le format attendu. Merci de vous rapporter au gabarit CSV disponible au téléchargement.',
    }
  }

  if (new Set(rows).size < rows.length) {
    const countByCode = rows.reduce<Record<string, number>>((acc, code) => {
      acc[code] = (acc[code] ?? 0) + 1
      return acc
    }, {})
    const codeNonUniques = [
      ...new Set(rows.filter((code) => (countByCode[code] ?? 0) > 1)),
    ]
    return {
      errorCode: ActivationCodeFileErrorCode.DUPLICATED_CODES,
      errorMessage: `Plusieurs codes identiques ont été trouvés dans le fichier : ${codeNonUniques
        .slice(0, MAX_CODE_DISPLAY)
        .join(', ')}${MAX_CODE_DISPLAY < codeNonUniques.length ? '... ' : ''}.`,
    }
  }

  return { activationCodes: rows }
}
