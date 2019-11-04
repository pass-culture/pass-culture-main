import { mapStateToProps } from '../MenuItemContainer'

describe('src | components | menu | MenuItemContainer', () => {
  let props
  let state

  beforeEach(() => {
    props = {
      item: {
        featureName: 'FOO',
      },
    }
    state = {
      data: {
        features: [],
      },
    }
  })

  describe('mapStateToProps()', () => {
    it('should return disabled when features are empty', () => {
      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        isDisabled: true,
      })
    })

    it('should return not disabled when no featureName', () => {
      // given
      state.data.features.push({ id: 'AE', isActive: true, nameKey: 'FOO' })
      props.featureName = undefined

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        isDisabled: false,
      })
    })

    it('should return disabled when no matching feature', () => {
      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        isDisabled: true,
      })
    })

    it('should return not disabled when active FAVORITE_OFFER', () => {
      // given
      state.data.features.push({ id: 'AE', isActive: true, nameKey: 'FOO' })

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        isDisabled: false,
      })
    })

    it('should return disabled when inactive FAVORITE_OFFER feature', () => {
      // given
      state.data.features.push({ id: 'AE', isActive: false, nameKey: 'FOO' })

      // when
      const result = mapStateToProps(state, props)

      // then
      expect(result).toStrictEqual({
        isDisabled: true,
      })
    })
  })
})
