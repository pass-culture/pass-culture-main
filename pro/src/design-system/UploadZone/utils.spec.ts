import { formatFileSize, getConditionsText } from './utils'

describe('formatFileSize', () => {
  it.each([
    [0, '0 o'],
    [999, '999 o'],
    [1_000, '1 ko'],
    [1_500, '1,5 ko'],
    [3_000_000, '3 Mo'],
    [2_540_000, '2,5 Mo'],
    [10_000_000, '10 Mo'],
    [1_200_000_000, '1,2 Go'],
  ])('should format %i bytes as "%s"', (bytes, expected) => {
    expect(formatFileSize(bytes)).toBe(expected)
  })
})

describe('getConditionsText', () => {
  it('should list the accepted extensions and the maximum size', () => {
    expect(
      getConditionsText(
        {
          'image/png': ['.png'],
          'image/jpeg': ['.jpeg'],
          'application/pdf': ['.pdf'],
        },
        5_000_000
      )
    ).toBe('Formats acceptés : PNG, JPEG, PDF. Poids maximum : 5 Mo.')
  })

  it('should not repeat an extension shared by several MIME types', () => {
    expect(
      getConditionsText({
        'text/csv': ['.csv'],
        'application/vnd.ms-excel': '.csv',
      })
    ).toBe('Formats acceptés : CSV.')
  })

  it('should only mention the maximum size when no format is given', () => {
    expect(getConditionsText(undefined, 1_000)).toBe('Poids maximum : 1 ko.')
  })

  it('should return an empty string without any constraint', () => {
    expect(getConditionsText()).toBe('')
  })
})
