import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import { MemoryRouter } from 'react-router-dom'
import NotificationMessage from '../Notification'
import { Provider } from 'react-redux'
import React from 'react'
import { configureTestStore } from 'store/testUtils'
import { queryByTextTrimHtml } from 'utils/testHelpers'

const renderNotificationMessage = ({ props, storeOverrides = {} }) => {
  const store = configureTestStore(storeOverrides)
  return render(
    <Provider store={store}>
      <MemoryRouter>
        <NotificationMessage {...props} />
      </MemoryRouter>
    </Provider>
  )
}

describe('src | components | pages | Venue | Notification', () => {
  const props = {
    dispatch: jest.fn(),
    venueId: 'TY',
    offererId: 'FT',
  }

  it('should display a succes messsage when venue is created', () => {
    const { debug } = renderNotificationMessage({ props })
    debug()
    expect(
      queryByTextTrimHtml(
        screen,
        'Lieu créé. Vous pouvez maintenant y créer une offre, ou en importer automatiquement.'
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText('créer une offre', { selector: 'a' })
    ).toHaveAttribute('href', '/offre/creation?lieu=TY&structure=FT')
  })
})
