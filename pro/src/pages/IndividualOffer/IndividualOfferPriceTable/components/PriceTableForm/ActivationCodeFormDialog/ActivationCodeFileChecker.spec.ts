import {
  checkAndParseUploadedFile,
  fileReader,
} from './ActivationCodeFileChecker'

describe('checkAndParseUploadedFile', () => {
  it('should raise an error when no file was provided', async () => {
    const { errorMessage } = await checkAndParseUploadedFile({
      fileReader,
      // @ts-expect-error to correct an error sentry where currentFile was not defined
      currentFile: undefined,
    })

    expect(errorMessage).toBe('Aucun fichier sélectionné.')
  })

  it('should raise an error when file is larger than MAX_FILE_SIZE', async () => {
    const biggerThan1Mo = new Blob([new Uint8Array(1024 * 1024 + 1)])

    const { errorMessage } = await checkAndParseUploadedFile({
      fileReader,
      currentFile: biggerThan1Mo,
    })

    expect(errorMessage).toBe('Le poids du fichier ne doit pas dépasser 1 Mo.')
  })

  it('should raise an error when file cannot be read', async () => {
    const currentFile = new Blob()

    const { errorMessage } = await checkAndParseUploadedFile({
      fileReader,
      currentFile,
    })

    expect(errorMessage).toBe(
      'Le fichier est vide ou illisible, veuillez réessayer ou contacter le support.'
    )
  })

  it('should raise an error when csv is empty', async () => {
    const emptyCsv = new Blob([], { type: 'text/csv' })

    const { errorMessage } = await checkAndParseUploadedFile({
      fileReader,
      currentFile: emptyCsv,
    })

    expect(errorMessage).toBe(
      'Le fichier est vide ou illisible, veuillez réessayer ou contacter le support.'
    )
  })

  it('should raise an error when csv is correct but with no values', async () => {
    const csv = new Blob([','], { type: 'text/csv' })

    const { errorMessage } = await checkAndParseUploadedFile({
      fileReader,
      currentFile: csv,
    })

    expect(errorMessage).toBe('Le fichier ne contient aucun code d’activation.')
  })

  it.each([
    ',',
    ';',
    '.',
  ])('should raise an error when CSV contains "%s"', async (c) => {
    const csv = new Blob([`${c}\n`], { type: 'text/csv' })

    const { errorMessage } = await checkAndParseUploadedFile({
      fileReader,
      currentFile: csv,
    })

    expect(errorMessage).toBe(
      'Le fichier ne respecte pas le format attendu. Merci de vous rapporter au gabarit CSV disponible au téléchargement.'
    )
  })

  it('should raise an error when csv is correct but with duplicates values', async () => {
    const csv = new Blob(['kikou_1\nkikou_2\nkikou_3\nkikou_2'], {
      type: 'text/csv',
    })

    const { errorMessage } = await checkAndParseUploadedFile({
      fileReader,
      currentFile: csv,
    })

    expect(errorMessage).toBe(
      'Plusieurs codes identiques ont été trouvés dans le fichier : kikou_2.'
    )
  })

  it('should return activation codes when csv has no errors', async () => {
    const csv = new Blob(['kikou_1\nkikou_2\nkikou_3\nkikou_4\n'], {
      type: 'text/csv',
    })

    const { errorMessage, activationCodes } = await checkAndParseUploadedFile({
      fileReader,
      currentFile: csv,
    })

    expect(errorMessage).toBe(undefined)
    expect(activationCodes).toStrictEqual([
      'kikou_1',
      'kikou_2',
      'kikou_3',
      'kikou_4',
    ])
  })
})
