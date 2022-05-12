import { requiredIfComponentHasProp } from 'utils/propTypes'

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

    it('should consider linked prop as given with some falsy values', () => {
      // Given
      componentProps[VALIDATING_PROP_NAME] = null
      const falsyLinkedPropValuesToConsiderGiven = ['', false]
      falsyLinkedPropValuesToConsiderGiven.forEach(falsyLinkedPropValue => {
        componentProps.href = falsyLinkedPropValue

        // When
        const error = requiredIfComponentHasProp('href', 'string')(
          componentProps,
          VALIDATING_PROP_NAME,
          componentName
        )

        // Then
        expect(error.message).toBe(
          'The prop `hrefName` is marked as required in `Banner`, but its value is `null`.'
        )
      })
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

    it('should not warn user when validating prop is given with some falsy values', () => {
      // Given
      const falsyPropValues = ['', false]
      falsyPropValues.forEach(falsyPropValue => {
        componentProps[VALIDATING_PROP_NAME] = falsyPropValue

        // When
        const error = requiredIfComponentHasProp('href', typeof falsyPropValue)(
          componentProps,
          VALIDATING_PROP_NAME,
          componentName
        )

        // Then
        expect(error).not.toBeInstanceOf(Error)
        expect(error).toBeUndefined()
      })
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

    it('should warn user that dependent prop type is wrong even with some falsy prop value', () => {
      // Given
      const falsyPropValues = ['', false]
      falsyPropValues.forEach(falsyPropValue => {
        componentProps[VALIDATING_PROP_NAME] = falsyPropValue

        // When
        const error = requiredIfComponentHasProp('href', 'number')(
          componentProps,
          VALIDATING_PROP_NAME,
          componentName
        )

        // Then
        expect(error).toBeInstanceOf(Error)
        expect(error.message).toBe(
          `Invalid prop \`hrefName\` of type \`${typeof falsyPropValue}\` supplied to \`Banner\`, expected \`number\`.`
        )
      })
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
