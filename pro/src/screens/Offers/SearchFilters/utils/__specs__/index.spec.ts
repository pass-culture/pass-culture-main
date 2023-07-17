import { cleanURLParam } from '../'

describe('cleanUrlParam', () => {
  it('should remove dangerous characters', () => {
    expect(cleanURLParam('hello(%$);,+=;{}: tout va bien/-')).toEqual(
      'hello, tout va bien/-'
    )
  })
  it('should return empty string when there is no param', () => {
    expect(cleanURLParam()).toEqual('')
  })
})
