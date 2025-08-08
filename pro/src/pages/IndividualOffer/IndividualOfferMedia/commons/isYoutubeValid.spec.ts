import { isYoutubeValid } from './isYoutubeValid'

describe('isYoutubeValid', () => {
  it('returns true for valid youtube URLs', () => {
    expect(isYoutubeValid('https://www.youtube.com/watch?v=abcdefghijk')).toBe(
      true
    )
    expect(isYoutubeValid('https://youtu.be/abcdefghijk')).toBe(true)
  })

  it('returns false for non-youtube URLs', () => {
    expect(isYoutubeValid('https://vimeo.com/12345')).toBe(false)
    expect(isYoutubeValid('https://www.dailymotion.com/video/x9negsq')).toBe(
      false
    )
  })

  it('returns false for invalid URLs', () => {
    expect(isYoutubeValid('not a url')).toBe(false)
    expect(isYoutubeValid('')).toBe(false)
    expect(isYoutubeValid(undefined)).toBe(false)
  })
})
