const { requiredIfComponentHasProp } = require('utils/propTypes')

const VALIDATING_PROP_NAME = 'hrefName'

describe('requiredIfComponentHasProp', () => {
  let componentName, componentProps
  beforeEach(() => {
    componentProps = {}
    componentName = 'Banner'
  })

  describe('when linked prop is given to component', () => {
    beforeEach(() => {
      componentProps.href = 'https://example.com'
    })

    it('should warn user when validating prop is missing', () => {
      // Given
      componentProps[VALIDATING_PROP_NAME] = null

      // When
      const error = requiredIfComponentHasProp('href', 'string')(
        componentProps,
        VALIDATING_PROP_NAME,
        componentName
      )

      // Then
      expect(error).toBeInstanceOf(Error)
      expect(error.message).toBe(
        'The prop `hrefName` is marked as required in `Banner`, but its value is `null`.'
      )
    })

    it('should warn user that dependent prop type is wrong', () => {
      // Given
      componentProps[VALIDATING_PROP_NAME] = 1234

      // When
      const error = requiredIfComponentHasProp('href', 'string')(
        componentProps,
        VALIDATING_PROP_NAME,
        componentName
      )

      // Then
      expect(error).toBeInstanceOf(Error)
      expect(error.message).toBe(
        'Invalid prop `hrefName` of type `number` supplied to `Banner`, expected `string`.'
      )
    })

    it('should not warn user when correct type', () => {
      // Given
      componentProps[VALIDATING_PROP_NAME] = 'Go to example'

      // When
      const error = requiredIfComponentHasProp('href', 'string')(
        componentProps,
        VALIDATING_PROP_NAME,
        componentName
      )

      // Then
      expect(error).not.toBeInstanceOf(Error)
      expect(error).toBeUndefined()
    })
  })

  describe('when linked prop is not given to component', () => {
    beforeEach(() => {
      componentProps.href = null
    })

    it('should not warn user when dependant prop is not given to component', () => {
      // When
      componentProps[VALIDATING_PROP_NAME] = null

      const error = requiredIfComponentHasProp('href', 'string')(
        componentProps,
        VALIDATING_PROP_NAME,
        componentName
      )

      // Then
      expect(error).not.toBeInstanceOf(Error)
      expect(error).toBeUndefined()
    })
  })
})
