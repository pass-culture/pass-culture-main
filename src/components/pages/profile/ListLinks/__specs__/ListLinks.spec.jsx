import { shallow } from 'enzyme'
import React from 'react'

import ListLinks from '../ListLinks'
import SignoutLinkContainer from '../../SignoutLink/SignoutLinkContainer'

describe('my informations', () => {
  let props

  beforeEach(() => {
    props = {
      historyPush: jest.fn(),
      readRecommendations: [],
    }
  })

  it('should display a link to personal informations page', () => {
    // When
    const wrapper = shallow(<ListLinks {...props} />)

    // Then
    const linkToPersonalInformationsPage = wrapper
      .find({ children: 'Informations personnelles' })
      .parent()
      .prop('to')

    expect(linkToPersonalInformationsPage).toBe('/profil/informations')
  })

  it('should display a link to password modification page', () => {
    // When
    const wrapper = shallow(<ListLinks {...props} />)

    // Then
    const linkToPasswordChangePage = wrapper
      .find({ children: 'Mot de passe' })
      .parent()
      .prop('to')

    expect(linkToPasswordChangePage).toBe('/profil/mot-de-passe')
  })

  it('should display a link to help page', () => {
    // When
    const wrapper = shallow(<ListLinks {...props} />)

    // Then
    const linkToHelpPage = wrapper.find({ children: 'Aide' }).parent()

    expect(linkToHelpPage.prop('href')).toBe(
      'https://aide.passculture.app/fr/category/18-ans-1dnil5r/'
    )
    expect(linkToHelpPage.prop('rel')).toBe('noopener noreferrer')
    expect(linkToHelpPage.prop('target')).toBe('_blank')
    expect(linkToHelpPage.prop('title')).toBe('Ouverture de l’aide dans une nouvelle fenêtre')
  })

  it('should display a signout link', () => {
    // When
    const wrapper = shallow(<ListLinks {...props} />)

    // Then
    const SignoutLink = wrapper.find(SignoutLinkContainer)
    expect(SignoutLink).toHaveLength(1)
  })
})
