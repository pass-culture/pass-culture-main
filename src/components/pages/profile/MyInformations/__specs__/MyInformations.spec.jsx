import { shallow } from 'enzyme'
import React from 'react'

import MyInformations from '../MyInformations'

describe('src | components | pages | profile | MyInformations | MyInformations', () => {
  it('should display a link to personal informations page', () => {
    // Given
    // When
    const wrapper = shallow(<MyInformations />)

    // Then
    const linkToPersonalInformationsPage = wrapper
      .find({ children: 'Informations personnelles' })
      .parent()
      .props()
      .to

    expect(linkToPersonalInformationsPage).toBe('/profil/informations')
  })

  it('should display a link to password modification page', () => {
    // Given
    // When
    const wrapper = shallow(<MyInformations />)

    // Then
    const linkToPasswordChangePage = wrapper
      .find({ children: 'Mot de passe' })
      .parent()
      .props()
      .to

    expect(linkToPasswordChangePage).toBe('/profil/password')
  })
})
