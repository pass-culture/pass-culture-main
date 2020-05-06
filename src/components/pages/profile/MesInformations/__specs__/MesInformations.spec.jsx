import { shallow } from 'enzyme'
import React from 'react'

import state from '../../../../../mocks/state'
import MesInformations from '../MesInformations'

describe('src | components | pages | profile | MesInformations | MesInformations', () => {
  it('should display a link to personal informations page', () => {
    // given
    const wrapper = shallow(
      <MesInformations
        getDepartment={jest.fn()}
        getFormValuesByNames={jest.fn()}
        handleSubmit={jest.fn()}
        user={state.user}
      />
    )

    // when
    const linkToPersonalInformationsPage = wrapper
      .find({ children: 'Informations personnelles' })
      .parent()

    // then
    expect(linkToPersonalInformationsPage.props().to).toBe('/profil/informations')
  })

  it('should display a link to password modification page', () => {
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
    const linkToPasswordChangePage = wrapper.find({ children: 'Mot de passe' }).parent()

    expect(linkToPasswordChangePage.props().to).toBe('/profil/password')
  })
})
