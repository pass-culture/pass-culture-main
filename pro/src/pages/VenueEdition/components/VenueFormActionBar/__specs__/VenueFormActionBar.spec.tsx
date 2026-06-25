import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
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
  it('should display the save button', () => {
    renderVenueFormActionBar({})
    expect(screen.getByText('Enregistrer')).toBeInTheDocument()
  })

  it('should display the cancel button', () => {
    renderVenueFormActionBar({})
    expect(screen.getByRole('button', { name: 'Annuler' })).toBeInTheDocument()
  })

  it('should call onCancel when cancel button is clicked', async () => {
    const onCancel = vi.fn()
    renderVenueFormActionBar({ onCancel })

    await userEvent.click(screen.getByRole('button', { name: 'Annuler' }))

    expect(onCancel).toHaveBeenCalledOnce()
  })
})
