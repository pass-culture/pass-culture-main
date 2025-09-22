import { getUrlYoutubeError } from './getUrlYoutubeError'

describe('getUrlYoutubeError', () => {
  it('returns nothing for valid youtube URLs', () => {
    expect(
      getUrlYoutubeError('https://www.youtube.com/watch?v=abcdefghijk')
    ).toBe(undefined)
    expect(getUrlYoutubeError('https://youtu.be/abcdefghijk')).toBe(undefined)
    expect(
      getUrlYoutubeError('http://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s')
    ).toBe(undefined)
    expect(getUrlYoutubeError('http://www.youtube.com/embed/dQw4w9WgXcQ')).toBe(
      undefined
    )
    expect(getUrlYoutubeError('http://youtube.com/v/dQw4w9WgXcQ')).toBe(
      undefined
    )
    expect(getUrlYoutubeError('https://www.youtube.com/e/dQw4w9WgXcQ')).toBe(
      undefined
    )
    expect(
      getUrlYoutubeError(
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PLUMRshJ8e2c4oQ60D4Ew15A1LgN5C7Y3X'
      )
    ).toBe(undefined)
    expect(getUrlYoutubeError('http://m.youtube.com/watch?v=dQw4w9WgXcQ')).toBe(
      undefined
    )
  })

  it('returns specific message for non-youtube URLs', () => {
    expect(getUrlYoutubeError('https://vimeo.com/12345')).toBe(
      'Veuillez renseigner une URL provenant de la plateforme Youtube'
    )
    expect(
      getUrlYoutubeError('https://www.dailymotion.com/video/x9negsq')
    ).toBe('Veuillez renseigner une URL provenant de la plateforme Youtube')
    // TODO: change error message
    expect(
      getUrlYoutubeError('https://www.youtube.com/shorts/dQw4w9WgXcQ')
    ).toBe('Veuillez renseigner une URL provenant de la plateforme Youtube')
    expect(getUrlYoutubeError('https://www.youtube.com/@Msnight_fall')).toBe(
      'Veuillez renseigner une URL provenant de la plateforme Youtube'
    )
  })

  it('returns false for invalid URLs', () => {
    expect(getUrlYoutubeError('not a url')).toBe(
      'Veuillez renseigner une URL valide. Ex : https://exemple.com'
    )
    expect(getUrlYoutubeError('')).toBe(
      'Veuillez renseigner une URL provenant de la plateforme Youtube'
    )
    expect(getUrlYoutubeError(undefined)).toBe(
      'Veuillez renseigner une URL provenant de la plateforme Youtube'
    )
  })
})
