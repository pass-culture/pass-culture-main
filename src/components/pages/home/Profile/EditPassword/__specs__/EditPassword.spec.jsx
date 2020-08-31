import { mount, shallow } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import HeaderContainer from '../../../../../layout/Header/HeaderContainer'
import EditPassword from '../EditPassword'

describe('edit password', () => {
  let event
  let props

  beforeEach(() => {
    event = { preventDefault: jest.fn() }
    props = {
      historyPush: jest.fn(),
      handleSubmit: jest.fn(),
      triggerSuccessSnackbar: jest.fn(),
      pathToProfile: '/profil',
      user: {
        password: 'correct password',
      },
    }
  })

  it('should display the header', () => {
    // When
    const wrapper = shallow(<EditPassword {...props} />)

    // Then
    const header = wrapper.find(HeaderContainer)
    expect(header.prop('backTo')).toBe('/profil')
    expect(header.prop('title')).toBe('Mot de passe')
  })

  it('should display password form', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <EditPassword {...props} />
      </MemoryRouter>
    )

    // Then
    const labels = wrapper.find('label')
    const currentPasswordLabel = labels.at(0).text()
    const newPasswordLabel = labels.at(1).text()
    const newConfirmationPasswordLabel = labels.at(2).text()
    expect(currentPasswordLabel).toBe('Mot de passe actuel')
    expect(newPasswordLabel).toBe('Nouveau mot de passe')
    expect(newConfirmationPasswordLabel).toBe('Confirmation nouveau mot de passe')

    const inputs = wrapper.find('input')
    const currentPassword = inputs.at(0).prop('type')
    const newPassword = inputs.at(1).prop('type')
    const newConfirmationPassword = inputs.at(2).prop('type')
    expect(currentPassword).toBe('password')
    expect(newPassword).toBe('password')
    expect(newConfirmationPassword).toBe('password')

    const buttons = wrapper.find('button')
    const currentPasswordButton = buttons.at(0).find('img[alt="Afficher le mot de passe"]')
    const newPasswordButton = buttons.at(1).find('img[alt="Afficher le mot de passe"]')
    const newConfirmationPasswordButton = buttons.at(2).find('img[alt="Afficher le mot de passe"]')
    expect(currentPasswordButton).toHaveLength(1)
    expect(newPasswordButton).toHaveLength(1)
    expect(newConfirmationPasswordButton).toHaveLength(1)

    const newPasswordPlaceholder = inputs.at(1).prop('placeholder')
    const newConfirmationPasswordPlaceholder = inputs.at(2).prop('placeholder')
    expect(newPasswordPlaceholder).toBe('Ex : m02pass!')
    expect(newConfirmationPasswordPlaceholder).toBe('Ex : m02pass!')

    const submitButton = wrapper.find('input[type="submit"]')
    expect(submitButton.prop('value')).toBe('Enregistrer')
  })

  describe('when click on submit button', () => {
    describe('while all fields are not completed', () => {
      it('should not be able to change password', () => {
        // given
        const wrapper = mount(
          <MemoryRouter>
            <EditPassword {...props} />
          </MemoryRouter>
        )

        const inputs = wrapper.find('input')
        const currentPassword = inputs.at(0)
        const newPassword = inputs.at(1)
        const form = wrapper.find('form')

        // when
        currentPassword.invoke('onChange')({ target: { value: 'current password' } })
        newPassword.invoke('onChange')({ target: { value: 'new password' } })
        form.invoke('onSubmit')(event)

        // then
        expect(props.handleSubmit).toHaveBeenCalledTimes(0)
      })
    })

    describe('when user has completed all fields properly', () => {
      it('should redirect to profile and call snackbar + API with proper informations', () => {
        // Given
        jest.spyOn(props, 'handleSubmit').mockImplementation((values, fail, success) => success())

        const wrapper = mount(
          <MemoryRouter>
            <EditPassword {...props} />
          </MemoryRouter>
        )
        const inputs = wrapper.find('input')
        const currentPassword = inputs.at(0)
        const newPassword = inputs.at(1)
        const newConfirmationPassword = inputs.at(2)
        const form = wrapper.find('form')

        // When
        currentPassword.invoke('onChange')({
          target: { value: 'current password', name: 'currentPassword' },
        })
        newPassword.invoke('onChange')({ target: { value: 'new password', name: 'newPassword' } })
        newConfirmationPassword.invoke('onChange')({
          target: { value: 'new password', name: 'newConfirmationPassword' },
        })
        form.invoke('onSubmit')(event)
        form.invoke('onSubmit')(event)

        // Then
        expect(props.historyPush).toHaveBeenCalledWith('/profil')
        expect(props.triggerSuccessSnackbar).toHaveBeenCalledTimes(1)
        expect(props.triggerSuccessSnackbar).toHaveBeenCalledWith(
          'Ton mot de passe a bien été modifié.'
        )
        expect(props.handleSubmit).toHaveBeenCalledWith(
          {
            newPassword: 'new password',
            newConfirmationPassword: 'new password',
            oldPassword: 'current password',
          },
          expect.any(Function),
          expect.any(Function)
        )
      })
    })

    describe('when fields are not valid', () => {
      it('should display error messages', () => {
        // Given
        const errors = {
          newPassword: ['Nouveau mot de passe invalide.'],
          newConfirmationPassword: ['Les deux mots de passe ne sont pas identiques.'],
          oldPassword: ['Ancien mot de passe incorrect.'],
        }

        jest.spyOn(props, 'handleSubmit').mockImplementation((values, fail) => fail(errors))

        const wrapper = mount(
          <MemoryRouter>
            <EditPassword {...props} />
          </MemoryRouter>
        )

        const inputs = wrapper.find('input')
        const oldPassword = inputs.at(0)
        const newPassword = inputs.at(1)
        const newConfirmationPassword = inputs.at(2)
        const form = wrapper.find('form')

        // When
        oldPassword.invoke('onChange')({
          target: { value: 'old password', name: 'currentPassword' },
        })
        newPassword.invoke('onChange')({ target: { value: 'new password', name: 'newPassword' } })
        newConfirmationPassword.invoke('onChange')({
          target: { value: 'wrong new password', name: 'newConfirmationPassword' },
        })
        form.invoke('onSubmit')(event)

        // Then
        const invalidNewPassword = wrapper.find({
          children: 'Nouveau mot de passe invalide.',
        })

        const missingCurrentPassword = wrapper.find({
          children: 'Les deux mots de passe ne sont pas identiques.',
        })

        const invalidOldPassword = wrapper.find({
          children: 'Ancien mot de passe incorrect.',
        })

        expect(invalidNewPassword).toHaveLength(1)
        expect(missingCurrentPassword).toHaveLength(1)
        expect(invalidOldPassword).toHaveLength(1)
      })
    })
  })
})
