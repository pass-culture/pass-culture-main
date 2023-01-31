import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'
import { queryByTextTrimHtml } from 'utils/testHelpers'

import NotificationMessage from '../Notification'

const renderNotificationMessage = props =>
  renderWithProviders(<NotificationMessage {...props} />)

describe('src | components | pages | Venue | Notification', () => {
  const props = {
    dispatch: jest.fn(),
    venueId: 'TY',
    offererId: 'FT',
  }

  it('should display a succes messsage when venue is created', () => {
    renderNotificationMessage(props)
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
