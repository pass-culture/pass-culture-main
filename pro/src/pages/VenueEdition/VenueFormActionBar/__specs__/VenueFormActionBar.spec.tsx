import { screen } from '@testing-library/react'
import { FormProvider, useForm } from 'react-hook-form'

import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import {
  VenueFormActionBar,
  VenueFormActionBarProps,
} from '../VenueFormActionBar'

function renderVenueFormActionBar(
  defaultProps: VenueFormActionBarProps,
  options?: RenderWithProvidersOptions
) {
  const Wrapper = () => {
    const methods = useForm({ defaultValues: {} })
    return (
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(() => {})}>
          <VenueFormActionBar {...defaultProps} />
        </form>
      </FormProvider>
    )
  }

  options = {
    user: sharedCurrentUserFactory(),
    features: ['WIP_ENABLE_NEW_OFFER_CREATION_JOURNEY'],
  }

  renderWithProviders(<Wrapper />, options)
}

describe('VenueFormActionBar', () => {
  it('should display right message on edition', () => {
    renderVenueFormActionBar({
      venue: { ...defaultGetVenue },
    })
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
