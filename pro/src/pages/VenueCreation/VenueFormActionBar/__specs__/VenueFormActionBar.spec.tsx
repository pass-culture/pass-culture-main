import { screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'

import { defaultGetVenue } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import {
  VenueFormActionBar,
  VenueFormActionBarProps,
} from '../VenueFormActionBar'

const renderVenueFormActionBar = (
  props: Partial<VenueFormActionBarProps> = {}
) => {
  renderWithProviders(
    <Formik initialValues={{}} onSubmit={vi.fn()}>
      <VenueFormActionBar {...props} />
    </Formik>,
    {
      user: sharedCurrentUserFactory(),
      features: ['WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'],
    }
  )
}

describe('VenueFormActionBar', () => {
  it('should display right message on edition', () => {
    renderVenueFormActionBar()
    expect(screen.getByText('Enregistrer')).toBeInTheDocument()
  })

  it('should display venue cancel link when not creating', () => {
    renderVenueFormActionBar({
      venue: { ...defaultGetVenue },
    })

    expect(screen.getByText('Annuler')).toHaveAttribute(
      'href',
      `/structures/${defaultGetVenue.managingOfferer.id}/lieux/${defaultGetVenue.id}`
    )
  })
})
