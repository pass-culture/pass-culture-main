import { mount, shallow } from 'enzyme'
import React from 'react'
import { MemoryRouter } from 'react-router'

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
      <MemoryRouter>
        <LegalNotice {...props} />
      </MemoryRouter>
    )

    // Then
    const termsAndConditionsPage = wrapper
      .find({ children: 'Conditions Générales d’Utilisation' })
      .parent()

    expect(termsAndConditionsPage.prop('href')).toBe('https://pass.culture.fr/cgu/')
    expect(termsAndConditionsPage.prop('rel')).toBe('noopener noreferrer')
    expect(termsAndConditionsPage.prop('target')).toBe('_blank')
    expect(termsAndConditionsPage.prop('title')).toBe(
      'Ouverture des Conditions Générales d’Utilisation dans une nouvelle page'
    )
  })

  it('should display a link to GDPR page', () => {
    // When
    const wrapper = mount(
      <MemoryRouter>
        <LegalNotice {...props} />
      </MemoryRouter>
    )

    // Then
    const gdprPage = wrapper
      .find({ children: 'Charte de protection des données personnelles' })
      .parent()

    expect(gdprPage.prop('href')).toBe('https://pass.culture.fr/donnees-personnelles/')
    expect(gdprPage.prop('rel')).toBe('noopener noreferrer')
    expect(gdprPage.prop('target')).toBe('_blank')
    expect(gdprPage.prop('title')).toBe(
      'Ouverture de la charte de protection des données personnelles dans une nouvelle page'
    )
  })

  it('should display a link to delete my account', () => {
    // Given
    const wrapper = mount(
      <MemoryRouter>
        <LegalNotice {...props} />
      </MemoryRouter>
    )

    // When
    const deleteAccountMailTo = wrapper.find({ children: 'Suppression du compte' }).parent()

    // Then
    expect(deleteAccountMailTo.prop('href')).toBe('mailto:deletionEmailAddress')
    expect(deleteAccountMailTo.prop('rel')).not.toBe('noopener noreferrer')
    expect(deleteAccountMailTo.prop('rel')).toBe('')
    expect(deleteAccountMailTo.prop('target')).not.toBe('_blank')
    expect(deleteAccountMailTo.prop('target')).toBe('')
    expect(deleteAccountMailTo.prop('title')).toBe('Envoyer un e-mail à support@passculture.app')
  })
})
