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
        isAdmin: true,
      },
    },
  }

  renderWithProviders(
    <Formik initialValues={{}} onSubmit={vi.fn()}>
      <VenueFormActionBar isCreatingVenue={isCreatingVenue} />
    </Formik>,
    { storeOverrides, features: ['WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'] }
  )
}

describe('VenueFormActionBar', () => {
  it('should display right message on edition', () => {
    renderVanueFormActionBar({ isCreatingVenue: false })
    expect(screen.getByText('Enregistrer et quitter')).toBeInTheDocument()
  })

  it('should display right message on creation', () => {
    renderVanueFormActionBar({ isCreatingVenue: true })
    expect(screen.getByText('Enregistrer et créer le lieu')).toBeInTheDocument()
  })
})
