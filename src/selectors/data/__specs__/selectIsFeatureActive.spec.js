import selectisFeatureActive from '../selectIsFeatureActive'

describe('src | components | router | selectors | selectisFeatureActive', () => {
  it('should return true when features is Empty', () => {
    // when
    const state = { data: { features: [] } }
    const featureName = null

    // when
    const isFeatureActive = selectisFeatureActive(state, featureName)

    // then
    expect(isFeatureActive).toStrictEqual(false)
  })

  it('should return true when featureName is falsy', () => {
    // when
    const state = { data: { features: [{ nameKey: 'FOO' }] } }
    const featureName = null

    // when
    const isFeatureActive = selectisFeatureActive(state, featureName)

    // then
    expect(isFeatureActive).toStrictEqual(false)
  })

  it('should return true when selected feature is not found', () => {
    // when
    const state = { data: { features: [{ nameKey: 'FOO' }] } }
    const featureName = 'BAR'

    // when
    const isFeatureActive = selectisFeatureActive(state, featureName)

    // then
    expect(isFeatureActive).toStrictEqual(false)
  })

  it('should return true when selected feature is not active', () => {
    // when
    const state = { data: { features: [{ isActive: false, nameKey: 'FOO' }] } }
    const featureName = 'FOO'

    // when
    const isFeatureActive = selectisFeatureActive(state, featureName)

    // then
    expect(isFeatureActive).toStrictEqual(false)
  })
})
