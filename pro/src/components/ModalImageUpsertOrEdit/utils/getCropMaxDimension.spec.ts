import { getCropMaxDimension } from './getCropMaxDimension'

describe('getCropMaxDimension', () => {
  it('should compute max width for original "landscape" target "landscape"', () => {
    const dimensions = getCropMaxDimension({
      originalDimensions: {
        width: 2000,
        height: 1000,
      },
      orientation: 'landscape',
    })
    expect(dimensions).toEqual({
      height: 1000,
      width: 1500,
    })
  })

  it('should compute max width for original "landscape" target "portrait"', () => {
    const dimensions = getCropMaxDimension({
      originalDimensions: {
        width: 2000,
        height: 1000,
      },
      orientation: 'portrait',
    })
    expect(dimensions).toEqual({
      height: 1000,
      width: 666,
    })
  })

  it('should compute max width for original "portrait" target "landscape"', () => {
    const dimensions = getCropMaxDimension({
      originalDimensions: {
        width: 1000,
        height: 2000,
      },
      orientation: 'landscape',
    })
    expect(dimensions).toEqual({
      height: 666,
      width: 1000,
    })
  })

  it('should compute max width for original "portrait" target "portrait"', () => {
    const dimensions = getCropMaxDimension({
      originalDimensions: {
        width: 1000,
        height: 2000,
      },
      orientation: 'portrait',
    })
    expect(dimensions).toEqual({
      width: 1000,
      height: 1500,
    })
  })
})
