import { searchPatternInOptions } from '../searchPatternInOptions'

describe('searchPatternInOptions', () => {
  it('should ignore heading and trailing spaces', () => {
    expect(
      searchPatternInOptions(['Le théâtre'], '  Le théâtre  ')
    ).toHaveLength(1)
  })

  it('should be case insensitive', () => {
    expect(searchPatternInOptions(['Le'], '  le  ')).toHaveLength(1)
    expect(searchPatternInOptions(['Le'], '  LE  ')).toHaveLength(1)
  })

  it('should match diacritics characters with regular characters', () => {
    expect(searchPatternInOptions(['Le théâtre'], 'Le theatre')).toHaveLength(1)

    expect(
      searchPatternInOptions(
        ['eéèêëaàâäiïînñcçEÉÈÊËAÀÂÄIÏÎNÑCÇ'],
        'eeeeeaaaaiiinncceeeeeaaaaiiinncc'
      )
    ).toHaveLength(1)
  })

  it('should match even if the pattern is not the beginning of the label', () => {
    expect(searchPatternInOptions(['Le théâtre'], 'theatre')).toHaveLength(1)
  })

  it('should match only if every word of the pattern were found in the label', () => {
    expect(
      searchPatternInOptions(['Le théâtre du Chatelet'], 'theatre chatelet')
    ).toHaveLength(1)

    expect(
      searchPatternInOptions(
        ['Le théâtre du Chatelet'],
        'theatre paris chatelet'
      )
    ).toHaveLength(0)
  })

  it('should limit the count of options outputed if the maxDisplayedCount is used', () => {
    expect(
      searchPatternInOptions(
        ['Le théâtre du Chatelet', 'Le théâtre du Chatelet 2'],
        'theatre chatelet'
      )
    ).toHaveLength(2)

    expect(
      searchPatternInOptions(
        ['Le théâtre du Chatelet', 'Le théâtre du Chatelet 2'],
        'theatre chatelet',
        1
      )
    ).toHaveLength(1)
  })
})
