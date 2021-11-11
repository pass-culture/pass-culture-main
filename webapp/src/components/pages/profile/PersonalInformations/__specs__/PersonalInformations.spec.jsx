import { mount, shallow } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

import HeaderContainer from '../../../../layout/Header/HeaderContainer'
import User from '../../ValueObjects/User'
import PersonalInformations from '../PersonalInformations'

describe('personal informations', () => {
  let event
  let props

  beforeEach(() => {
    event = { preventDefault: jest.fn() }
    props = {
      historyPush: jest.fn(),
      department: 'Seine-Saint' + '-Denis (93)',
      updateCurrentUser: jest.fn(),
      triggerSuccessSnackbar: jest.fn(),
      pathToProfile: '/profil',
      user: new User({
        publicName: 'Martino',
        firstName: 'Martin',
        lastName: 'Dupont',
        email: 'm.dupont@example.com',
      }),
    }
  })

  it("should display beneficiary's profile informations", () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <PersonalInformations {...props} />
      </MemoryRouter>
    )

    // Then
    const labels = wrapper.find('label')
    const nicknameLabel = labels.at(0).text()
    const nameLabel = labels.at(1).text()
    const emailLabel = labels.at(2).text()
    const departmentCodeLabel = labels.at(3).text()
    expect(nicknameLabel).toBe('Pseudo')
    expect(nameLabel).toBe('Nom et prénom')
    expect(emailLabel).toBe('Adresse e-mail')
    expect(departmentCodeLabel).toBe('Département de résidence')
    const inputs = wrapper.find('input')
    const nickname = inputs.at(0).prop('value')
    const name = inputs.at(1).prop('value')
    const email = inputs.at(2).prop('value')
    const departmentCode = inputs.at(3).prop('value')
    expect(nickname).toBe('Martino')
    expect(name).toBe('Martin Dupont')
    expect(email).toBe('m.dupont@example.com')
    expect(departmentCode).toBe('Seine-Saint-Denis (93)')
  })

  it('should display the header', () => {
    // When
    const wrapper = shallow(<PersonalInformations {...props} />)

    // Then
    const header = wrapper.find(HeaderContainer)
    expect(header.prop('backTo')).toBe('/profil')
    expect(header.prop('title')).toBe('Informations personnelles')
  })

  it('should prevent name, email and department code modifications', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <PersonalInformations {...props} />
      </MemoryRouter>
    )

    // Then
    const publicName = wrapper.find("input[value='Martino']")
    const name = wrapper.find("input[value='Martin Dupont']")
    const email = wrapper.find("input[value='m.dupont@example.com']")
    const departmentCode = wrapper.find("input[value='Seine-Saint-Denis (93)']")
    expect(publicName.prop('disabled')).toBe(false)
    expect(name.prop('disabled')).toBe(true)
    expect(email.prop('disabled')).toBe(true)
    expect(departmentCode.prop('disabled')).toBe(true)
  })

  describe('when click on submit button', () => {
    describe('when user has not modified his nickname', () => {
      it('should redirect to profile without submitting information', () => {
        // Given
        const wrapper = mount(
          <MemoryRouter>
            <PersonalInformations {...props} />
          </MemoryRouter>
        )
        const submitButton = wrapper.find('input[value="Enregistrer"]')

        // When
        submitButton.invoke('onClick')({ preventDefault: jest.fn() })

        // Then
        expect(props.updateCurrentUser).not.toHaveBeenCalled()
        expect(props.historyPush).toHaveBeenCalledWith('/profil')
      })
    })

    describe('when user has modified his nickname', () => {
      it('should redirect to profile and call snackbar once with proper informations', async () => {
        // Given
        jest.spyOn(props, 'updateCurrentUser').mockImplementation(() => null)

        const wrapper = mount(
          <MemoryRouter>
            <PersonalInformations {...props} />
          </MemoryRouter>
        )

        const nickname = wrapper.find('input[value="Martino"]')
        const form = wrapper.find('form')

        // When
        nickname.invoke('onChange')({ target: { value: 'DifferentNickname' } })
        await form.invoke('onSubmit')(event)

        // Then
        expect(props.historyPush).toHaveBeenCalledWith('/profil')
        expect(props.triggerSuccessSnackbar).toHaveBeenCalledTimes(1)
        expect(props.triggerSuccessSnackbar).toHaveBeenCalledWith('Ton pseudo a bien été modifié.')
      })
    })

    describe('when input nickname value is not valid', () => {
      it('should display an error message', () => {
        // Given
        jest.spyOn(props, 'updateCurrentUser').mockImplementation(() => {
          const errors = { publicName: ['Pseudo invalide'] }
          throw errors
        })
        const wrapper = mount(
          <MemoryRouter>
            <PersonalInformations {...props} />
          </MemoryRouter>
        )
        const nickname = wrapper.find("input[value='Martino']")
        const submitButton = wrapper.find('input[value="Enregistrer"]')

        // When
        nickname.invoke('onChange')({ target: { value: 'AA' } })
        submitButton.invoke('onClick')({ preventDefault: jest.fn() })

        // Then
        const wrongNickname = wrapper.find({ children: 'Pseudo invalide' })
        expect(wrongNickname).toHaveLength(1)
      })
    })
  })
})
