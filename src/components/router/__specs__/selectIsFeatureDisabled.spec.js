import selectIsFeatureDisabled from '../selectIsFeatureDisabled'

describe('src | components | router | selectIsFeatureDisabled', () => {
  it('should return true when null features', () => {
    // when
    const state = { data: { features: null } }
    const featureName = null

    // when
    const result = selectIsFeatureDisabled(state, featureName)

    // then
    const expected = true
    expect(result).toStrictEqual(expected)
  })

  it('should return false when null featureName', () => {
    // when
    const state = { data: { features: [{ name: 'FOO' }] } }
    const featureName = null

    // when
    const result = selectIsFeatureDisabled(state, featureName)

    // then
    const expected = false
    expect(result).toStrictEqual(expected)
  })

  it('should return false when selected feature is not found', () => {
    // when
    const state = { data: { features: [{ name: 'FOO' }] } }
    const featureName = 'BAR'

    // when
    const result = selectIsFeatureDisabled(state, featureName)

    // then
    const expected = false
    expect(result).toStrictEqual(expected)
  })

  it('should return true when selected feature is not active', () => {
    // when
    const state = { data: { features: [{ isActive: false, name: 'FOO' }] } }
    const featureName = 'FOO'

    // when
    const result = selectIsFeatureDisabled(state, featureName)

    // then
    const expected = true
    expect(result).toStrictEqual(expected)
  })
})
