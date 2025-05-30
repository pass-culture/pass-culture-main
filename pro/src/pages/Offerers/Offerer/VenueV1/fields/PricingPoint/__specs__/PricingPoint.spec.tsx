import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'
import { expect } from 'vitest'

import { api } from 'apiClient/api'
import * as useNotification from 'commons/hooks/useNotification'
import { defaultGetVenue } from 'commons/utils/factories/collectiveApiFactories'
import {
  defaultGetOffererResponseModel,
  defaultGetOffererVenueResponseModel,
} from 'commons/utils/factories/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'commons/utils/renderWithProviders'

import { PricingPoint, PricingPointProps } from '../PricingPoint'

vi.mock('apiClient/api', () => ({
  api: {
    linkVenueToPricingPoint: vi.fn(),
  },
}))

function renderPricingPoints(
  defaultProps: PricingPointProps,
  options?: RenderWithProvidersOptions
) {
  const Wrapper = () => {
    const methods = useForm({ defaultValues: {} })
    return (
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(() => {})}>
          <PricingPoint {...defaultProps} />
        </form>
      </FormProvider>
    )
  }

  renderWithProviders(<Wrapper />, options)
}

describe('PricingPoint', () => {
  const defaultProps: PricingPointProps = {
    offerer: {
      ...defaultGetOffererResponseModel,
      managedVenues: [
        { ...defaultGetOffererVenueResponseModel, siret: '12345678900001' },
      ],
    },
    venue: { ...defaultGetVenue, pricingPoint: null },
  }

  it('should call api when selecting new pricing point', async () => {
    renderPricingPoints(defaultProps)

    await userEvent.selectOptions(
      screen.getByLabelText(
        'Structure avec SIRET utilisée pour le calcul de votre barème de remboursement *'
      ),
      '1'
    )

    await userEvent.click(
      screen.getByRole('button', { name: 'Valider la sélection' })
    )

    await userEvent.click(
      screen.getByRole('button', {
        name: 'Valider ma sélection',
      })
    )

    expect(api.linkVenueToPricingPoint).toHaveBeenCalled()
  })

  it('should display error message when api call fail', async () => {
    vi.spyOn(api, 'linkVenueToPricingPoint').mockRejectedValue({
      response: { data: { message: 'error' } },
    })
    const mockNotifyError = vi.fn()
    const notifsImport = (await vi.importActual(
      'commons/hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: mockNotifyError,
    }))

    renderPricingPoints(defaultProps)

    await userEvent.selectOptions(
      screen.getByLabelText(
        'Structure avec SIRET utilisée pour le calcul de votre barème de remboursement *'
      ),
      '1'
    )
    await userEvent.click(
      screen.getByRole('button', { name: 'Valider la sélection' })
    )
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Valider ma sélection',
      })
    )

    expect(mockNotifyError).toHaveBeenCalledWith(
      'Une erreur est survenue lors de la sauvegarde de vos modifications.\n Merci de réessayer plus tard'
    )
  })
})
