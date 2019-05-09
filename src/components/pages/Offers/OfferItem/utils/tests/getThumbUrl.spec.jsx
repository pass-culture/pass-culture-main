import getThumbUrl from '../getThumbUrl'

describe('getThumbUrl', () => {
  it('should return an empty string when no mediations are given', () => {
    // given
    const mediations = null

    // when
    const result = getThumbUrl(mediations)

    // then
    expect(result).toBe('')
  })

  it('should return an empty string when mediations are empty', () => {
    // given
    const mediations = []

    // when
    const result = getThumbUrl(mediations)

    // then
    expect(result).toBe('')
  })

  it('should return url of thumb when mediations are given', () => {
    // given
    const mediations = [{ thumbUrl: 'fake url' }]

    // when
    const result = getThumbUrl(mediations)

    // then
    expect(result).toBe('fake url')
  })
})
