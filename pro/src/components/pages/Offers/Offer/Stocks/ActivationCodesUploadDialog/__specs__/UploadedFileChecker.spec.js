import {
  checkAndParseUploadedFile,
  csvToRows,
  fileReader,
} from '../UploadedFileChecker'

describe('uploadedFileChecker', () => {
  describe('csvToRows', () => {
    it.each`
      testName       | fileContent
      ${'null'}      | ${null}
      ${'undefined'} | ${undefined}
    `(
      'should return no rows from a $testName fileContent',
      async ({ fileContent }) => {
        // When
        const rows = csvToRows(fileContent)

        // then
        expect(rows).toHaveLength(0)
      }
    )

    it.each`
      fileContent
      ${''}
      ${'No Carriage Return in this file'}
    `(
      'should return no rows if fileContent does not contains a carriage return',
      async ({ fileContent }) => {
        // When
        const rows = csvToRows(fileContent)

        // then
        expect(rows).toHaveLength(0)
      }
    )

    it('should split a file content in rows', () => {
      // Given
      const fileContent = 'CD1122\nCD1114'

      // When
      const rows = csvToRows(fileContent)

      // then
      expect(rows).toStrictEqual(['CD1122', 'CD1114'])
    })

    it('should split a file content in rows and trim whitespaces', () => {
      // Given
      const fileContent = ' CD1122\nCD1114  '

      // When
      const rows = csvToRows(fileContent)

      // then
      expect(rows).toStrictEqual(['CD1122', 'CD1114'])
    })
  })

  describe('checkAndParseUploadedFile Method', () => {
    it('should return an error message if the file is bigger then 1 Mo', async () => {
      // When
      const currentFile = { size: 1048577 }
      const { errorMessage } = await checkAndParseUploadedFile({ currentFile })

      // then
      expect(errorMessage).toBe(
        'Le poids du fichier ne doit pas dépasser 1 Mo.'
      )
    })
    it('should return an error message if the file is not readable', async () => {
      // When
      const currentFile = { size: 1024 }
      const { errorMessage } = await checkAndParseUploadedFile({
        fileReader: () => Promise.resolve(null),
        currentFile,
      })

      // then
      expect(errorMessage).toBe(
        'Le fichier est vide ou illisible, veuillez réessayer ou contacter le support.'
      )
    })
    it('should return an error message if the file does not contain any activation code', async () => {
      // When
      const currentFile = { size: 1024 }
      const { errorMessage } = await checkAndParseUploadedFile({
        fileReader: () => Promise.resolve('\n \n \n'),
        currentFile,
      })

      // then
      expect(errorMessage).toBe(
        'Le fichier ne contient aucun code d’activation.'
      )
    })
    it('should return an error message if the file has more than 1 column per row', async () => {
      // When
      const currentFile = { size: 1024 }
      const { errorMessage } = await checkAndParseUploadedFile({
        fileReader: () => Promise.resolve('Code1\nCode3,Code4'),
        currentFile,
      })

      // then
      expect(errorMessage).toBe(
        'Le fichier ne respecte pas le format attendu. Merci de vous rapporter au gabarit CSV disponible au téléchargement.'
      )
    })
    it('should return an error message if the file contains duplicates (up to 5 are displayed)', async () => {
      // When
      const currentFile = { size: 1024 }
      const { errorMessage } = await checkAndParseUploadedFile({
        fileReader: () =>
          Promise.resolve(
            'C1\nC1\nC1\nC2\nC3\nC4\nC5\nC6\nC7\nC1\nC2\nC3\nC4\nC5\nC6'
          ),
        currentFile,
      })

      // then
      expect(errorMessage).toBe(
        'Plusieurs codes identiques ont été trouvés dans le fichier : C1, C2, C3, C4, C5... .'
      )
    })
    it.each`
      unauthorizedCharacter
      ${'.'}
      ${','}
      ${';'}
    `(
      'should return an error message if the file contains unauthorized characters ($unauthorizedCharacter) more than 1 column per row',
      async ({ unauthorizedCharacter }) => {
        // When
        const currentFile = { size: 1024 }
        const { errorMessage } = await checkAndParseUploadedFile({
          fileReader: () =>
            Promise.resolve(
              `C1\nC1\nC1\nC2\nC3${unauthorizedCharacter}\nC4\nC5\nC6\nC7\nC1\nC2\nC3\nC4\nC5\nC6`
            ),
          currentFile,
        })

        // then
        expect(errorMessage).toBe(
          'Le fichier ne respecte pas le format attendu. Merci de vous rapporter au gabarit CSV disponible au téléchargement.'
        )
      }
    )
    it('should return activation codes if the file is correct', async () => {
      // When
      const currentFile = { size: 1024 }
      const { errorMessage, activationCodes } = await checkAndParseUploadedFile(
        {
          fileReader: () =>
            Promise.resolve('ABOCADEAU_RJ3IF962W1\nABO#@235$01_3I62A4W'),
          currentFile,
        }
      )

      // then
      expect(errorMessage).toBeUndefined()
      expect(activationCodes).toStrictEqual([
        'ABOCADEAU_RJ3IF962W1',
        'ABO#@235$01_3I62A4W',
      ])
    })
  })

  describe('fileReader', () => {
    it('should return the content of a file as string', async () => {
      // Given
      const file = new File(
        ['ABH\nJHB\nJHB\nCEG\nCEG'],
        'activation_codes.csv',
        {
          type: 'text/csv',
        }
      )

      // When
      const content = await fileReader(file)

      // Then
      expect(content).toBe('ABH\nJHB\nJHB\nCEG\nCEG')
    })
  })
})
