import { pick } from '../pick'

describe('pick', () => {
  it('should reurn a new object with existing keys ', () => {
    // given
    const object = {
      key1: 'data',
      key2: 'other data',
      key3: 'an other data',
    }
    const keys = ['key1', 'key3', 'wrong key']

    // when
    const result = pick(object, keys)

    // then
    expect(result).toStrictEqual({
      key1: 'data',
      key3: 'an other data',
    })
  })

  it('should return nothing when there is no key', () => {
    // given
    const object = {
      key1: 'data',
    }
    const keys = []

    // when
    const result = pick(object, keys)

    // then
    expect(result).toStrictEqual({})
  })
})
