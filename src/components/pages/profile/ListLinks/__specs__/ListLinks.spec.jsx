import { shallow, mount } from 'enzyme'
import React from 'react'
import { Router } from 'react-router'
import { Provider } from 'react-redux'
import { createMemoryHistory } from 'history'

import ListLinks from '../ListLinks'
import SignoutLinkContainer from '../../SignoutLink/SignoutLinkContainer'
import getMockStore from '../../../../../utils/mockStore'

describe('my informations', () => {
  let props

  beforeEach(() => {
    props = {
      historyPush: jest.fn(),
      readRecommendations: [],
    }
  })

  it('should display a link to personal informations page', () => {
    // Given
    const mockStore = getMockStore({
      data: (
        state = {
          readRecommendations: [],
        }
      ) => state,
    })

    // When
    const wrapper = mount(
      <Provider store={mockStore}>
        <Router history={createMemoryHistory()}>
          <ListLinks {...props} />
        </Router>
      </Provider>
    )

    // Then
    const linkToPersonalInformationsPage = wrapper
      .find({ children: 'Informations personnelles' })
      .parent()
      .prop('href')

    expect(linkToPersonalInformationsPage).toBe('/profil/informations')
  })

  it('should display a link to password modification page', () => {
    // Given
    const mockStore = getMockStore({
      data: (
        state = {
          readRecommendations: [],
        }
      ) => state,
    })

    // When
    const wrapper = mount(
      <Provider store={mockStore}>
        <Router history={createMemoryHistory()}>
          <ListLinks {...props} />
        </Router>
      </Provider>
    )

    // Then
    const linkToPasswordChangePage = wrapper
      .find({ children: 'Mot de passe' })
      .parent()
      .prop('href')

    expect(linkToPasswordChangePage).toBe('/profil/mot-de-passe')
  })

  it('should display a link to help page', () => {
    // Given
    const mockStore = getMockStore({
      data: (
        state = {
          readRecommendations: [],
        }
      ) => state,
    })

    // When
    const wrapper = mount(
      <Provider store={mockStore}>
        <Router history={createMemoryHistory()}>
          <ListLinks {...props} />
        </Router>
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
    // Given
    const mockStore = getMockStore({
      data: (
        state = {
          readRecommendations: [],
        }
      ) => state,
    })

    // When
    const wrapper = mount(
      <Provider store={mockStore}>
        <Router history={createMemoryHistory()}>
          <ListLinks {...props} />
        </Router>
      </Provider>
    )

    // Then
    const legalNoticePage = wrapper
      .find({ children: 'Mentions légales' })
      .parent()
      .prop('href')

    expect(legalNoticePage).toBe('/profil/mentions-legales')
  })

  it('should display a signout link', () => {
    // When
    const wrapper = shallow(<ListLinks {...props} />)

    // Then
    const SignoutLink = wrapper.find(SignoutLinkContainer)
    expect(SignoutLink).toHaveLength(1)
  })
})
