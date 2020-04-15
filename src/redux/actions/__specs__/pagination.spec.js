import { updatePage, updateSeed, updateSeedLastRequestTimestamp } from '../pagination'

describe('actions | pagination', () => {
  it('should return an action of type UPDATE_PAGE', () => {
    // given
    const page = 1

    // when
    const result = updatePage(page)

    // then
    expect(result).toStrictEqual({
      page: 1,
      type: 'UPDATE_PAGE'
    })
  })

  it('should return an action of type UPDATE_SEED', () => {
    // given
    const seed = 0.5

    // when
    const result = updateSeed(seed)

    // then
    expect(result).toStrictEqual({
      seed: 0.5,
      type: 'UPDATE_SEED'
    })
  })

  it('should return an action of type UPDATE_SEED_LAST_REQUEST_TIMESTAMP', () => {
    // given
    const timestamp = 1574186119058

    // when
    const result = updateSeedLastRequestTimestamp(timestamp)

    // then
    expect(result).toStrictEqual({
      seedLastRequestTimestamp: 1574186119058,
      type: 'UPDATE_SEED_LAST_REQUEST_TIMESTAMP'
    })
  })
})
