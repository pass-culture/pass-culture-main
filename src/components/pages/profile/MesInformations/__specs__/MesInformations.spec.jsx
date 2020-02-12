import { mount, shallow } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import state from '../../../../../mocks/state'
import MesInformations from '../MesInformations'

describe('src | components | pages | profile | MesInformations | MesInformations', () => {
  it('should display profile informations', () => {
    // When
    const wrapper = mount(
      <Router history={createBrowserHistory()}>
        <MesInformations
          getDepartment={jest.fn()}
          getFormValuesByNames={jest.fn()}
          handleSubmit={jest.fn()}
          user={state.user}
        />
      </Router>
    )

    // Then
    const publicNameLabel = wrapper.find({ children: 'Identifiant' })
    const nameLabel = wrapper.find({ children: 'Nom et prénom' })
    const emailLabel = wrapper.find({ children: 'Adresse e-mail' })
    const departmentCodeLabel = wrapper.find({ children: 'Département de résidence' })
    const passwordLabel = wrapper.find({ children: 'Mot de passe' })
    expect(publicNameLabel).toHaveLength(1)
    expect(nameLabel).toHaveLength(1)
    expect(emailLabel).toHaveLength(1)
    expect(departmentCodeLabel).toHaveLength(1)
    expect(passwordLabel).toHaveLength(1)
  })

  it("should display beneficiary's profile informations", () => {
    // Given
    const user = { ...state.user }
    user.publicName = 'Martino'
    user.firstName = 'Martin'
    user.lastName = 'Dupont'
    user.email = 'm.dupont@test.com'
    user.departementCode = '93'
    const mockedGetDepartment = jest.fn().mockReturnValue('Seine-Saint-Denis (93)')

    // When
    const wrapper = mount(
      <Router history={createBrowserHistory()}>
        <MesInformations
          getDepartment={mockedGetDepartment}
          getFormValuesByNames={jest.fn()}
          handleSubmit={jest.fn()}
          user={user}
        />
      </Router>
    )

    // Then
    const publicName = wrapper.find("input[value='Martino']")
    const name = wrapper.find("input[value='Martin Dupont']")
    const email = wrapper.find("input[value='m.dupont@test.com']")
    const departmentCode = wrapper.find("input[value='Seine-Saint-Denis (93)']")
    expect(publicName).toHaveLength(1)
    expect(name).toHaveLength(1)
    expect(email).toHaveLength(1)
    expect(departmentCode).toHaveLength(1)
  })

  it('should prevent name, email and departmentCode modifications', () => {
    // Given
    const user = { ...state.user }
    user.publicName = 'Martino'
    user.firstName = 'Martin'
    user.lastName = 'Dupont'
    user.email = 'm.dupont@test.com'
    user.departementCode = '93'
    const mockedGetDepartment = jest.fn().mockReturnValue('Seine-Saint-Denis (93)')

    // When
    const wrapper = mount(
      <Router history={createBrowserHistory()}>
        <MesInformations
          getDepartment={mockedGetDepartment}
          getFormValuesByNames={jest.fn()}
          handleSubmit={jest.fn()}
          user={user}
        />
      </Router>
    )

    // Then
    const publicName = wrapper.find("input[value='Martino']")
    const name = wrapper.find("input[value='Martin Dupont']")
    const email = wrapper.find("input[value='m.dupont@test.com']")
    const departmentCode = wrapper.find("input[value='Seine-Saint-Denis (93)']")
    expect(publicName.props().disabled).toBe(false)
    expect(name.props().disabled).toBe(true)
    expect(email.props().disabled).toBe(true)
    expect(departmentCode.props().disabled).toBe(true)
  })

  it('should go to password modification page on button click', () => {
    // When
    const wrapper = shallow(
      <MesInformations
        getDepartment={jest.fn()}
        getFormValuesByNames={jest.fn()}
        handleSubmit={jest.fn()}
        user={state.user}
      />
    )

    // Then
    const passwordChangeButton = wrapper.find({ children: 'Changer mon mot de passe' })
    expect(passwordChangeButton).toHaveLength(1)
    const passwordChangeUrl = passwordChangeButton.props().to
    expect(passwordChangeUrl).toBe('/profil/password')
  })

  it('should save form modifications when user leaves input field', () => {
    // Given
    const mockedHandleSubmit = jest.fn()
    const user = { ...state.user }
    user.publicName = 'Martino'
    const mockedFormValues = jest.fn().mockReturnValue({ publicName: user.publicName })

    const wrapper = mount(
      <Router history={createBrowserHistory()}>
        <MesInformations
          getDepartment={jest.fn()}
          getFormValuesByNames={mockedFormValues}
          handleSubmit={mockedHandleSubmit}
          user={user}
        />
      </Router>
    )
    const publicNameInput = wrapper.find("input[name='publicName']")
    const form = wrapper.find('form')

    // When
    publicNameInput.simulate('blur', { target: { form: form } })

    // Then
    expect(mockedHandleSubmit).toHaveBeenCalledTimes(1)
    expect(mockedHandleSubmit).toHaveBeenCalledWith(
      {
        publicName: user.publicName,
      },
      expect.any(Function),
      expect.any(Function)
    )
  })
})
