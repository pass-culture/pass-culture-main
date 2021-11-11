import selectIsFeatureDisabled from '../selectIsFeatureDisabled'

describe('src | components | router | selectIsFeatureDisabled', () => {
  it('should return true when features is Empty', () => {
    // when
    const state = { data: { features: [] } }
    const featureName = null

    // when
    const isFeatureDisabled = selectIsFeatureDisabled(state, featureName)

    // then
    expect(isFeatureDisabled).toStrictEqual(true)
  })

  it('should return true when featureName is falsy', () => {
    // when
    const state = { data: { features: [{ nameKey: 'FOO' }] } }
    const featureName = null

    // when
    const isFeatureDisabled = selectIsFeatureDisabled(state, featureName)

    // then
    expect(isFeatureDisabled).toStrictEqual(true)
  })

  it('should return true when selected feature is not found', () => {
    // when
    const state = { data: { features: [{ nameKey: 'FOO' }] } }
    const featureName = 'BAR'

    // when
    const isFeatureDisabled = selectIsFeatureDisabled(state, featureName)

    // then
    expect(isFeatureDisabled).toStrictEqual(true)
  })

  it('should return true when selected feature is not active', () => {
    // when
    const state = { data: { features: [{ isActive: false, nameKey: 'FOO' }] } }
    const featureName = 'FOO'

    // when
    const isFeatureDisabled = selectIsFeatureDisabled(state, featureName)

    // then
    expect(isFeatureDisabled).toStrictEqual(true)
  })
})
