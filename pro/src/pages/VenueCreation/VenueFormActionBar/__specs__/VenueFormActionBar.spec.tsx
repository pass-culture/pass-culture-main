import { screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'

import { defaultGetVenue } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  VenueFormActionBar,
  VenueFormActionBarProps,
} from '../VenueFormActionBar'

const renderVenueFormActionBar = (props: Partial<VenueFormActionBarProps>) => {
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
      <VenueFormActionBar {...props} />
    </Formik>,
    { storeOverrides, features: ['WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'] }
  )
}

describe('VenueFormActionBar', () => {
  it('should display right message on edition', () => {
    renderVenueFormActionBar({ isCreatingVenue: false })
    expect(screen.getByText('Enregistrer et quitter')).toBeInTheDocument()
  })

  it('should display right message on creation', () => {
    renderVenueFormActionBar({ isCreatingVenue: true })
    expect(screen.getByText('Enregistrer et créer le lieu')).toBeInTheDocument()
  })

  it('should display venue cancel link when not creating', () => {
    renderVenueFormActionBar({
      isCreatingVenue: false,
      venue: { ...defaultGetVenue },
    })

    expect(screen.getByText('Annuler et quitter')).toHaveAttribute(
      'href',
      `/structures/${defaultGetVenue.managingOfferer.id}/lieux/${defaultGetVenue.id}`
    )
  })
})
