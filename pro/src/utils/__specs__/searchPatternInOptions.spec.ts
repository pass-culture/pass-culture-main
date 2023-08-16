import { searchPatternInOptions } from '../searchPatternInOptions'

describe('searchPatternInOptions', () => {
  it('should ignore heading and trailing spaces', () => {
    expect(
      searchPatternInOptions(
        [{ label: 'Le théâtre', value: '' }],
        '  Le théâtre  '
      )
    ).toHaveLength(1)
  })

  it('should be case insensitive', () => {
    expect(
      searchPatternInOptions([{ label: 'Le', value: '' }], '  le  ')
    ).toHaveLength(1)

    expect(
      searchPatternInOptions([{ label: 'le', value: '' }], '  LE  ')
    ).toHaveLength(1)
  })

  it('should match diacritics characters with regular characters', () => {
    expect(
      searchPatternInOptions([{ label: 'Le théâtre', value: '' }], 'Le theatre')
    ).toHaveLength(1)

    expect(
      searchPatternInOptions(
        [{ label: 'eéèêëaàâäiïînñcçEÉÈÊËAÀÂÄIÏÎNÑCÇ', value: '' }],
        'eeeeeaaaaiiinncceeeeeaaaaiiinncc'
      )
    ).toHaveLength(1)
  })

  it('should match even if the pattern is not the beginning of the label', () => {
    expect(
      searchPatternInOptions([{ label: 'Le théâtre', value: '' }], 'theatre')
    ).toHaveLength(1)
  })
})
