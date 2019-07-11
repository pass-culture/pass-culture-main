import { computeNewZoom } from 'components/layout/UploadThumb'

const defaultParams = {
  current: 0.3,
  min: 0.1,
  max: 3,
  step: 0.01,
  factor: 10,
  direction: 1,
}

describe('src | components | pages | Offer | UploadThumb | computeZoom', () => {
  it('should return a bigger zoom', () => {
    // given
    const { current, min, max, step, factor, direction } = defaultParams

    // when
    const newZoom = computeNewZoom(current, min, max, step, factor, direction)

    // then
    expect(newZoom).toBeDefined()
    expect(newZoom).toBeGreaterThan(current)
  })

  it('should return a smaller zoom', () => {
    // given
    const { current, min, max, step, factor } = defaultParams
    const direction = -1

    // when
    const newZoom = computeNewZoom(current, min, max, step, factor, direction)

    // then
    expect(newZoom).toBeDefined()
    expect(newZoom).toBeLessThan(current)
  })

  it('should not return zoom smaller than min', () => {
    // given
    const { min, max, step, factor } = defaultParams
    const current = min + step
    const direction = -1

    // when
    const newZoom = computeNewZoom(current, min, max, step, factor, direction)

    // then
    expect(newZoom).toBeDefined()
    expect(newZoom).toStrictEqual(current)
  })

  it('should not return zoom greater than max', () => {
    // given
    const { min, max, step, factor, direction } = defaultParams
    const current = max - step

    // when
    const newZoom = computeNewZoom(current, min, max, step, factor, direction)

    // then
    expect(newZoom).toBeDefined()
    expect(newZoom).toStrictEqual(current)
  })
})
