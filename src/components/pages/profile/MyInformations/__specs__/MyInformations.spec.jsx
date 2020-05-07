import { shallow } from 'enzyme'
import React from 'react'

import MyInformations from '../MyInformations'

describe('my informations', () => {
  it('should display a link to personal informations page', () => {
    // When
    const wrapper = shallow(<MyInformations />)

    // Then
    const linkToPersonalInformationsPage = wrapper
      .find({ children: 'Informations personnelles' })
      .parent()
      .prop('to')

    expect(linkToPersonalInformationsPage).toBe('/profil/informations')
  })

  it('should display a link to password modification page', () => {
    // When
    const wrapper = shallow(<MyInformations />)

    // Then
    const linkToPasswordChangePage = wrapper
      .find({ children: 'Mot de passe' })
      .parent()
      .prop('to')

    expect(linkToPasswordChangePage).toBe('/profil/password')
  })
})
