import { mount } from 'enzyme'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router-dom'

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
    const link = textMessage.find({ children: 'créer une offre' }).at(1)

    // then
    expect(textMessage.text()).toBe(
      'Lieu créé. Vous pouvez maintenant y créer une offre, ou en importer automatiquement. '
    )
    expect(link.prop('href')).toBe('/offre/creation?lieu=TY&structure=FT')
  })
})
