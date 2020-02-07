import { mapDispatchToProps, mapStateToProps } from '../MesInformationsContainer'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')

  return {
    requestData,
  }
})

jest.mock('with-react-redux-login', () => ({
  resolveCurrentUser: 'current beneficiary',
}))

describe('src | components | pages | profile | MesInformations | MesInformationsContainer', () => {
  describe('mapStateToProps', () => {
    it('should return given props', () => {
      // Given
      const givenProps = {
        existing: 'prop',
      }

      // When
      const props = mapStateToProps({}, givenProps)

      // Then
      expect(props).toStrictEqual(givenProps)
    })
  })

  describe('mapDispatchToProps', () => {
    it('should return props containing a handleSubmit function', () => {
      // When
      const props = mapDispatchToProps()

      // Then
      expect(props.handleSubmit).toBeDefined()
      expect(typeof props.handleSubmit).toBe('function')
    })

    describe('handleSubmit', () => {
      it('should call dispatch with request data', () => {
        // Given
        const dispatch = jest.fn()
        const payload = {
          publicName: 'Beneficiary',
        }
        const failureCallback = jest.fn()
        const successCallback = jest.fn()

        // When
        mapDispatchToProps(dispatch).handleSubmit(payload, failureCallback, successCallback)

        // Then
        expect(dispatch).toHaveBeenCalledWith({
          config: {
            apiPath: 'users/current',
            body: {
              publicName: 'Beneficiary',
            },
            handleFail: failureCallback,
            handleSuccess: successCallback,
            method: 'PATCH',
            key: 'user',
            resolve: 'current beneficiary',
          },
          type: 'REQUEST_DATA_PATCH_USERS/CURRENT',
        })
      })
    })
  })
})
