import { resolveCurrentUser } from '../../../../../selectors/data/usersSelectors'
import getDepartementByCode from '../../../../../utils/getDepartementByCode'
import {
  getDepartment,
  getFormValuesByNames,
  mapDispatchToProps,
  mapStateToProps,
} from '../MesInformationsContainer'

jest.mock('redux-thunk-data', () => {
  const { requestData } = jest.requireActual('fetch-normalize-data')

  return {
    requestData,
  }
})

jest.mock('../../../../../utils/getDepartementByCode')

describe('src | components | pages | profile | MesInformations | MesInformationsContainer', () => {
  describe('getFormValuesByNames', () => {
    it('should get form values for non disabled fields', () => {
      // Given
      const formInputEvent = {
        target: {
          form: [
            {
              name: 'identifiant',
              value: 'Martino',
              disabled: false,
            },
            {
              name: 'name',
              value: 'Martin',
              disabled: true,
            },
            {
              name: 'departementCode',
              value: '94',
              disabled: false,
            },
          ],
        },
      }

      // When
      const formValuesByNames = getFormValuesByNames(formInputEvent)

      // Then
      expect(formValuesByNames).toStrictEqual({
        identifiant: 'Martino',
        departementCode: '94',
      })
    })
  })

  describe('getDepartment', () => {
    it('should return department name and department code given the department code', () => {
      // Given
      const departmentCode = '93'
      getDepartementByCode.mockReturnValue('Seine-Saint-Denis')

      // When
      const result = getDepartment(departmentCode)

      // Then
      expect(result).toBe('Seine-Saint-Denis (93)')
    })
  })

  describe('mapStateToProps', () => {
    it('should pass user to MesInformations component', () => {
      // Given
      const user = { id: 'userId' }
      const state = { data: { users: [user] } }

      // When
      const props = mapStateToProps(state)

      // Then
      expect(props).toStrictEqual({
        getDepartment: expect.any(Function),
        getFormValuesByNames: expect.any(Function),
        user,
      })
    })
  })

  describe('mapDispatchToProps', () => {
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
            resolve: resolveCurrentUser,
          },
          type: 'REQUEST_DATA_PATCH_USERS/CURRENT',
        })
      })
    })
  })
})
