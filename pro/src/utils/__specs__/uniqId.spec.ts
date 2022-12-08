import { uniqId } from 'utils/uniqId'

describe('uniqId', () => {
  it('should return a random string', () => {
    expect(uniqId().length).toBe(5)

    // Very unlikely to have a collision
    expect(uniqId()).not.toBe(uniqId())
  })
})
