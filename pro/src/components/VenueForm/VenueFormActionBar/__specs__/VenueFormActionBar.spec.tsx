import { screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { VenueFormActionBar } from '../index'

const renderVanueFormActionBar = ({
  isCreatingVenue,
}: {
  isCreatingVenue: boolean
}) => {
  const storeOverrides = {
    user: {
      initialized: true,
      currentUser: {
        nonHumanizedId: 12,
        isAdmin: true,
      },
    },
    features: {
      list: [
        {
          nameKey: 'WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY',
          isActive: true,
        },
      ],
      initialized: true,
    },
  }

  renderWithProviders(
    <Formik initialValues={{}} onSubmit={jest.fn()}>
      <VenueFormActionBar isCreatingVenue={isCreatingVenue} offererId={59} />
    </Formik>,
    { storeOverrides }
  )
}

describe('VenueFormActionBar', () => {
  it('should display right message on edition', async () => {
    renderVanueFormActionBar({ isCreatingVenue: false })
    expect(screen.getByText('Enregistrer et quitter')).toBeInTheDocument()
  })

  it('should display right message on creation', async () => {
    renderVanueFormActionBar({ isCreatingVenue: true })
    expect(screen.getByText('Enregistrer et créer le lieu')).toBeInTheDocument()
  })
})
