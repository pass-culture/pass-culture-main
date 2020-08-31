import { computeEndValidityDate } from '../computeEndValidityDate'

describe('computeEndValidityDate', () => {
  it('should return formatted date', () => {
    // given
    const date = '2019-09-10T08:05:45.778894Z'

    // when
    const formattedDate = computeEndValidityDate(date)

    // then
    expect(formattedDate).toBe('10/09/2021')
  })
})
