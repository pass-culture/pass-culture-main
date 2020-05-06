import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import state from '../../../../../mocks/state'
import PersonalInformations from '../PersonalInformations'

describe('src | components | pages | profile | PersonalInformations | PersonalInformations', () => {
  let props
  let history
  const user = { ...state.user }

  user.publicName = 'Martino'
  user.firstName = 'Martin'
  user.lastName = 'Dupont'
  user.email = 'm.dupont@test.com'
  user.departementCode = '93'

  const mockedGetDepartment = jest.fn().mockReturnValue('Seine-Saint-Denis (93)')

  beforeEach(() => {
    history = {
      push: jest.fn(),
    }

    props = {
      history,
      getDepartment: mockedGetDepartment,
      handleSubmit: jest.fn(),
      toast: jest.fn(),
      pathToProfile: '/profil',
      user: user,
    }
  })

  it('should display profile informations', () => {
    // Given - When
    const wrapper = mount(
      <Router history={createBrowserHistory()}>
        <PersonalInformations {...props} />
      </Router>
    )

    // Then
    const publicNameLabel = wrapper.find({ children: 'Pseudo' })
    const nameLabel = wrapper.find({ children: 'Nom et prénom' })
    const emailLabel = wrapper.find({ children: 'Adresse e-mail' })
    const departmentCodeLabel = wrapper.find({ children: 'Département de résidence' })
    expect(publicNameLabel).toHaveLength(1)
    expect(nameLabel).toHaveLength(1)
    expect(emailLabel).toHaveLength(1)
    expect(departmentCodeLabel).toHaveLength(1)
  })

  it("should display beneficiary's profile informations", () => {
    // Given - When
    const wrapper = mount(
      <Router history={createBrowserHistory()}>
        <PersonalInformations {...props} />
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
    // Given - When
    const wrapper = mount(
      <Router history={createBrowserHistory()}>
        <PersonalInformations {...props} />
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

  describe('when click on submit button', () => {
    describe('when user has not modified his name', () => {
      it('should redirect to profile without submitting information', () => {
        // Given
        const spyHistory = jest.spyOn(history, 'push')

        const wrapper = mount(
          <Router history={createBrowserHistory()}>
            <PersonalInformations {...props} />
          </Router>
        )

        const submitButton = wrapper.find({ children: 'Enregistrer' })

        // When
        submitButton.simulate('click')

        // Then
        expect(props.handleSubmit).not.toHaveBeenCalled()
        expect(spyHistory).toHaveBeenCalledWith('/profil')
      })
    })

    describe('when user has modified his name', () => {
      it('should submit information', () => {
        // Given
        const wrapper = mount(
          <Router history={createBrowserHistory()}>
            <PersonalInformations {...props} />
          </Router>
        )

        const publicName = wrapper.find("input[value='Martino']")
        const submitButton = wrapper.find({ children: 'Enregistrer' })

        // When
        publicName.simulate('change', { target: { value: 'DifferentName' } })
        submitButton.simulate('click')

        // Then
        expect(props.handleSubmit).toHaveBeenCalledTimes(1)
        expect(props.handleSubmit).toHaveBeenCalledWith(
          {
            publicName: 'DifferentName',
          },
          expect.any(Function),
          expect.any(Function)
        )
      })
    })
  })
})
