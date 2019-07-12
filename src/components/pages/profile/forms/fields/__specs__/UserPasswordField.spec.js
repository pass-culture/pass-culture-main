import React from 'react'
import { shallow } from 'enzyme'
import { UserPasswordField } from '../UserPasswordField'
import { FormError } from '../../../../../forms'
import { validateMatchingFields } from '../../../../../forms/validators'
import { PasswordField } from '../../../../../forms/inputs'

jest.mock('../../../../../forms/validators', () => ({
  validateMatchingFields: jest.fn(),
}))
describe('src | components | pages | profile | forms | fields | UserPasswordField', () => {
  let props

  beforeEach(() => {
    props = {
      isLoading: false,
    }
  })

  it('should match snapshot', () => {
    // when
    const wrapper = shallow(<UserPasswordField {...props} />)

    // then
    expect(wrapper).toBeDefined()
    expect(wrapper).toMatchSnapshot()
  })

  it('should render three UserPasswordField components', () => {
    // when
    const wrapper = shallow(<UserPasswordField {...props} />)

    // then
    const passwordFields = wrapper.find(PasswordField)
    expect(passwordFields).toHaveLength(3)
    expect(passwordFields.at(0).prop('required')).toStrictEqual(expect.any(Function))
    expect(passwordFields.at(0).prop('name')).toBe('oldPassword')
    expect(passwordFields.at(0).prop('disabled')).toBe(false)
    expect(passwordFields.at(0).prop('label')).toBe('Saisissez votre mot de passe actuel')
    expect(passwordFields.at(1).prop('required')).toBe(true)
    expect(passwordFields.at(1).prop('className')).toBe('mt36')
    expect(passwordFields.at(1).prop('name')).toBe('newPassword')
    expect(passwordFields.at(1).prop('disabled')).toBe(false)
    expect(passwordFields.at(1).prop('label')).toBe('Saisissez votre nouveau mot de passe')
    expect(passwordFields.at(2).prop('required')).toStrictEqual(expect.any(Function))
    expect(passwordFields.at(2).prop('className')).toBe('mt36')
    expect(passwordFields.at(2).prop('name')).toBe('newPasswordConfirm')
    expect(passwordFields.at(2).prop('disabled')).toBe(false)
    expect(passwordFields.at(2).prop('label')).toBe('Confirmez votre nouveau mot de passe')
  })

  it('should render a FormError component when errors', () => {
    // given
    props.formErrors = 'error1'

    // when
    const wrapper = shallow(<UserPasswordField {...props} />)

    // then
    const formError = wrapper.find(FormError)
    expect(formError).toHaveLength(1)
    expect(formError.prop('customMessage')).toBe('error1')
  })

  describe('functions', () => {
    describe('buildOldPasswordLabel', () => {
      it('should return undefined when old password is provided', () => {
        // given
        const wrapper = shallow(<UserPasswordField {...props} />)

        // when
        const result = wrapper.instance().buildOldPasswordLabel()('fake label')

        // then
        expect(result).toBeUndefined()
      })

      it('should return missing old password message when old password is not provided', () => {
        // given
        const wrapper = shallow(<UserPasswordField {...props} />)

        // when
        const result = wrapper.instance().buildOldPasswordLabel()()

        // then
        expect(result).toBe("L'ancien mot de passe est manquant.")
      })
    })

    describe('validateNewPassword', () => {
      it('should validate new password when provided', () => {
        // given
        const newPasswordConfirm = 'hello'
        const formValues = {
          newPassword: 'hello',
        }
        const wrapper = shallow(<UserPasswordField {...props} />)

        // when
        wrapper.instance().validateNewPassword()(newPasswordConfirm, formValues)

        // then
        expect(validateMatchingFields).toHaveBeenCalledWith('hello', 'hello')
      })
    })
  })
})
