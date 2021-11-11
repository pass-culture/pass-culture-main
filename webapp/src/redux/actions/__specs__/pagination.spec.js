import { updateSeedLastRequestTimestamp } from '../pagination'

describe('actions | pagination', () => {
  it('should return an action of type UPDATE_SEED_LAST_REQUEST_TIMESTAMP', () => {
    // given
    const timestamp = 1574186119058

    // when
    const result = updateSeedLastRequestTimestamp(timestamp)

    // then
    expect(result).toStrictEqual({
      seedLastRequestTimestamp: 1574186119058,
      type: 'UPDATE_SEED_LAST_REQUEST_TIMESTAMP',
    })
  })
})
