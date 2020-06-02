import { mount, shallow } from 'enzyme'
import { createMemoryHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import HeaderContainer from '../../../../layout/Header/HeaderContainer'
import LegalNotice from '../LegalNotice'

jest.mock('../../domain/getAccountDeletionEmail', () => ({
  getAccountDeletionEmail: jest.fn(() => 'mailto:deletionEmailAddress'),
}))

describe('legal notice page', () => {
  let props
  beforeEach(() => {
    props = {
      historyPush: jest.fn(),
      pathToProfile: 'path/to/profile',
      userEmail: 'user@example.com',
    }
  })

  it('should display the header', () => {
    // When
    const wrapper = shallow(<LegalNotice {...props} />)

    // Then
    const header = wrapper.find(HeaderContainer)
    expect(header.prop('backTo')).toBe('path/to/profile')
    expect(header.prop('title')).toBe('Mentions Légales')
  })

  it('should display a link to terms and conditions page', () => {
    // When
    const wrapper = mount(
      <Router history={createMemoryHistory()}>
        <LegalNotice {...props} />
      </Router>
    )

    // Then
    const termsAndConditionsPage = wrapper
      .find({ children: 'Conditions Générales d’Utilisation' })
      .parent()

    expect(termsAndConditionsPage.prop('href')).toBe(
      'https://docs.passculture.app/textes-normatifs/mentions-legales-et-conditions-generales-dutilisation-de-lapplication-pass-culture'
    )
    expect(termsAndConditionsPage.prop('rel')).toBe('noopener noreferrer')
    expect(termsAndConditionsPage.prop('target')).toBe('_blank')
    expect(termsAndConditionsPage.prop('title')).toBe(
      'Ouverture des Conditions Générales d’Utilisation dans une nouvelle page'
    )
  })

  it('should display a link to GDPR page', () => {
    // When
    const wrapper = mount(
      <Router history={createMemoryHistory()}>
        <LegalNotice {...props} />
      </Router>
    )

    // Then
    const gdprPage = wrapper
      .find({ children: 'Charte de protection des données personnelles' })
      .parent()

    expect(gdprPage.prop('href')).toBe(
      'https://docs.passculture.app/textes-normatifs/charte-des-donnees-personnelles'
    )
    expect(gdprPage.prop('rel')).toBe('noopener noreferrer')
    expect(gdprPage.prop('target')).toBe('_blank')
    expect(gdprPage.prop('title')).toBe(
      'Ouverture de la charte de protection des données personnelles dans une nouvelle page'
    )
  })

  it('should display a link to delete my account', () => {
    // Given
    const wrapper = mount(
      <Router history={createMemoryHistory()}>
        <LegalNotice {...props} />
      </Router>
    )

    // When
    const deleteAccountMailTo = wrapper.find({ children: 'Suppression du compte' }).parent()

    // Then
    expect(deleteAccountMailTo.prop('href')).toBe('mailto:deletionEmailAddress')
    expect(deleteAccountMailTo.prop('rel')).toBe('noopener noreferrer')
    expect(deleteAccountMailTo.prop('title')).toBe('Envoyer un e-mail à support@passculture.app')
  })
})
