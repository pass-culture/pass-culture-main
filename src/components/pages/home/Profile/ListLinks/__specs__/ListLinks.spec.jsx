import { mount } from 'enzyme'
import React from 'react'
import { Provider } from 'react-redux'
import { MemoryRouter } from 'react-router'

import { getStubStore } from '../../../../../../utils/stubStore'
import ListLinks from '../ListLinks'

describe('my informations', () => {
  let mockStore
  let props

  beforeEach(() => {
    mockStore = getStubStore({
      data: (
        state = {
          readRecommendations: [],
        }
      ) => state,
    })

    props = {
      historyPush: jest.fn(),
    }
  })

  it('should display a link to personal informations page', () => {
    // When
    const wrapper = mount(
      <Provider store={mockStore}>
        <MemoryRouter>
          <ListLinks {...props} />
        </MemoryRouter>
      </Provider>
    )

    // Then
    const linkToPersonalInformationsPage = wrapper
      .find({ children: 'Informations personnelles' })
      .parent()
      .prop('href')

    expect(linkToPersonalInformationsPage).toBe('/accueil/profil/informations')
  })

  it('should display a link to password modification page', () => {
    // When
    const wrapper = mount(
      <Provider store={mockStore}>
        <MemoryRouter>
          <ListLinks {...props} />
        </MemoryRouter>
      </Provider>
    )

    // Then
    const linkToPasswordChangePage = wrapper
      .find({ children: 'Mot de passe' })
      .parent()
      .prop('href')

    expect(linkToPasswordChangePage).toBe('/accueil/profil/mot-de-passe')
  })

  it('should display a link to help page', () => {
    // When
    const wrapper = mount(
      <Provider store={mockStore}>
        <MemoryRouter>
          <ListLinks {...props} />
        </MemoryRouter>
      </Provider>
    )

    // Then
    const linkToHelpPage = wrapper.find({ children: 'Aide' }).parent()

    expect(linkToHelpPage.prop('href')).toBe(
      'https://aide.passculture.app/fr/category/18-ans-1dnil5r/'
    )
    expect(linkToHelpPage.prop('rel')).toBe('noopener noreferrer')
    expect(linkToHelpPage.prop('target')).toBe('_blank')
    expect(linkToHelpPage.prop('title')).toBe('Ouverture de l’aide dans une nouvelle fenêtre')
  })

  it('should display a link to legal notice page', () => {
    // When
    const wrapper = mount(
      <Provider store={mockStore}>
        <MemoryRouter>
          <ListLinks {...props} />
        </MemoryRouter>
      </Provider>
    )

    // Then
    const legalNoticePage = wrapper
      .find({ children: 'Mentions légales' })
      .parent()
      .prop('href')

    expect(legalNoticePage).toBe('/accueil/profil/mentions-legales')
  })

  it('should display a sign out link', () => {
    // When
    const wrapper = mount(
      <Provider store={mockStore}>
        <MemoryRouter>
          <ListLinks {...props} />
        </MemoryRouter>
      </Provider>
    )

    // Then
    const signOutLink = wrapper
      .find({ children: 'Déconnexion' })
      .parent()
      .prop('href')
    expect(signOutLink).toBe('')
  })
})
