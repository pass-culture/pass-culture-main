import { screen } from '@testing-library/react'
import { FormProvider, useForm } from 'react-hook-form'

import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import {
  type RenderWithProvidersOptions,
  renderWithProviders,
} from '@/commons/utils/renderWithProviders'

import {
  VenueFormActionBar,
  type VenueFormActionBarProps,
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
  }

  renderWithProviders(<Wrapper />, options)
}

describe('VenueFormActionBar', () => {
  it('should display right message on edition', () => {
    renderVenueFormActionBar({})
    expect(screen.getByText('Enregistrer')).toBeInTheDocument()
  })

  it('should display venue cancel link when not creating', () => {
    renderVenueFormActionBar({})

    expect(screen.getByRole('link', { name: 'Annuler' })).toHaveAttribute(
      'href',
      `/partenaire/page-individuelle`
    )
  })
})
