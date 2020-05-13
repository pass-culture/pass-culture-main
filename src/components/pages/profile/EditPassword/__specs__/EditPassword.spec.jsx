import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import EditPassword from '../EditPassword'
import HeaderContainer from '../../../../layout/Header/HeaderContainer'

describe('edit password', () => {
  let props

  beforeEach(() => {
    props = {
      history: {
        push: jest.fn(),
      },
      handleSubmit: jest.fn(),
      snackbar: jest.fn(),
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
    expect(header.prop('closeTo')).toBeNull()
    expect(header.prop('title')).toBe('Mot de passe')
  })

  it('should display password form', () => {
    // When
    const wrapper = mount(
      <Router history={createBrowserHistory()}>
        <EditPassword {...props} />
      </Router>
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
    describe('when user has modified his password', () => {
      it('should redirect to profile and call snackbar with proper informations', () => {
        // Given
        jest.spyOn(props, 'handleSubmit').mockImplementation((values, fail, success) => success())

        const wrapper = mount(
          <Router history={createBrowserHistory()}>
            <EditPassword {...props} />
          </Router>
        )
        const inputs = wrapper.find('input')
        const currentPassword = inputs.at(0)
        const newPassword = inputs.at(1)
        const newConfirmationPassword = inputs.at(2)
        const submitButton = wrapper.find('input[value="Enregistrer"]')

        // When
        currentPassword.invoke('onChange')({ target: { value: 'current password' } })
        newPassword.invoke('onChange')({ target: { value: 'new password' } })
        newConfirmationPassword.invoke('onChange')({ target: { value: 'new password' } })
        submitButton.invoke('onClick')({ preventDefault: jest.fn() })

        // Then
        expect(props.history.push).toHaveBeenCalledWith('/profil')
        expect(props.snackbar).toHaveBeenCalledWith(
          'Ton mot de passe a bien été modifié.',
          'success'
        )
        expect(props.handleSubmit).toHaveBeenCalledWith(
          {
            newPassword: 'new password',
            oldPassword: 'current password',
          },
          expect.any(Function),
          expect.any(Function)
        )
      })
    })

    describe('when clicking on submit button', () => {
      it('should call API with proper parameters', () => {
        // Given
        const wrapper = mount(
          <Router history={createBrowserHistory()}>
            <EditPassword {...props} />
          </Router>
        )
        const inputs = wrapper.find('input')
        const currentPassword = inputs.at(0)
        const newPassword = inputs.at(1)
        const newConfirmationPassword = inputs.at(2)
        const submitButton = wrapper.find('input[value="Enregistrer"]')

        // When
        currentPassword.invoke('onChange')({ target: { value: 'current password' } })
        newPassword.invoke('onChange')({ target: { value: 'new password' } })
        newConfirmationPassword.invoke('onChange')({ target: { value: 'new password' } })
        submitButton.invoke('onClick')({ preventDefault: jest.fn() })

        // Then
        expect(props.handleSubmit).toHaveBeenCalledWith(
          {
            newPassword: 'new password',
            oldPassword: 'current password',
          },
          expect.any(Function),
          expect.any(Function)
        )
      })
    })

    describe('when new password and confirmation password are not the same', () => {
      it('should display an error message', () => {
        // Given
        const wrapper = mount(
          <Router history={createBrowserHistory()}>
            <EditPassword {...props} />
          </Router>
        )
        const inputs = wrapper.find('input')
        const newPassword = inputs.at(1)
        const newConfirmationPassword = inputs.at(2)
        const submitButton = wrapper.find('input[value="Enregistrer"]')

        // When
        newPassword.invoke('onChange')({ target: { value: 'new password' } })
        newConfirmationPassword.invoke('onChange')({ target: { value: 'wrong new password' } })
        submitButton.invoke('onClick')({ preventDefault: jest.fn() })

        // Then
        const missingCurrentPassword = wrapper.find({
          children: 'Les deux mots de passe ne sont pas identiques.',
        })
        expect(missingCurrentPassword).toHaveLength(1)
      })
    })
  })
})
