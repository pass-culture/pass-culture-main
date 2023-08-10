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

  it('should match if at least one word from the pattern is in the label', () => {
    expect(
      searchPatternInOptions(
        [{ label: 'Le théâtre', value: '' }],
        'un theatre à Paris'
      )
    ).toHaveLength(1)
  })

  it('should sort filtered options based on number of matched in label', () => {
    const filteredOptions = searchPatternInOptions(
      [
        { label: 'Le théâtre de Brest', value: '' },
        { label: 'Cinéma de Nantes', value: '' },
        { label: 'Le théâtre de paris', value: '' },
      ],
      'theatre Paris'
    )
    expect(filteredOptions).toHaveLength(2)
    expect(filteredOptions[0].label).toEqual('Le théâtre de paris')
  })
})
