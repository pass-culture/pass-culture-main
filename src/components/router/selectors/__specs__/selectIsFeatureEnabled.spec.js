import selectIsFeatureEnabled from '../selectIsFeatureEnabled'

describe('src | components | router | selectIsFeatureEnabled', () => {
  it('should return false when features is Empty', () => {
    // when
    const state = { data: { features: [] } }
    const featureName = null

    // when
    const isFeatureDisabled = selectIsFeatureEnabled(state, featureName)

    // then
    expect(isFeatureDisabled).toStrictEqual(false)
  })

  it('should return false when featureName is falsy', () => {
    // when
    const state = { data: { features: [{ nameKey: 'FOO' }] } }
    const featureName = null

    // when
    const isFeatureDisabled = selectIsFeatureEnabled(state, featureName)

    // then
    expect(isFeatureDisabled).toStrictEqual(false)
  })

  it('should return false when selected feature is not found', () => {
    // when
    const state = { data: { features: [{ nameKey: 'FOO' }] } }
    const featureName = 'BAR'

    // when
    const isFeatureDisabled = selectIsFeatureEnabled(state, featureName)

    // then
    expect(isFeatureDisabled).toStrictEqual(false)
  })

  it('should return false when selected feature is not active', () => {
    // when
    const state = { data: { features: [{ isActive: false, nameKey: 'FOO' }] } }
    const featureName = 'FOO'

    // when
    const isFeatureDisabled = selectIsFeatureEnabled(state, featureName)

    // then
    expect(isFeatureDisabled).toStrictEqual(false)
  })
})
