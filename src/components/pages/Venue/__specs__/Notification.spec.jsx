import { mount } from 'enzyme'
import React from 'react'
import { NavLink, Router } from 'react-router-dom'
import { createBrowserHistory } from 'history'
import NotificationMessage from '../Notification'

describe('src | components | pages | Venue | Notification', () => {
  const props = {
    dispatch: jest.fn(),
    venueId: 'TY',
    offererId: 'FT',
  }

  it('should display a succes messsage when venue is created', () => {
    // given
    const history = createBrowserHistory()

    // when
    const wrapper = mount(
      <Router history={history}>
        <NotificationMessage {...props} />
      </Router>
    )
    const textMessage = wrapper.find('p')
    const navLink = wrapper.find(NavLink)

    // then
    expect(textMessage.text()).toBe(
      'Lieu créé. Vous pouvez maintenant y créer une offre, ou en importer automatiquement. '
    )
    expect(navLink.props().to).toBe('/offres/creation?lieu=TY&structure=FT')
  })
})
