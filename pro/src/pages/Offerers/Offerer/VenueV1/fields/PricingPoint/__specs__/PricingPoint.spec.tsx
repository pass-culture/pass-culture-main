import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'
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
  renderWithProviders(
    <Formik initialValues={{}} onSubmit={() => {}}>
      <PricingPoint {...defaultProps} />
    </Formik>,
    options
  )
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
        'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement *'
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
        'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement *'
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

  describe('OA feature flag', () => {
    it('should display the right wording without the OA FF', async () => {
      renderPricingPoints(defaultProps)

      expect(
        screen.getByText('Sélectionner un lieu dans la liste')
      ).toBeInTheDocument()

      expect(
        screen.getByText(
          'Comment ajouter vos coordonnées bancaires sur un lieu sans SIRET ?'
        )
      ).toBeInTheDocument()

      expect(
        screen.getByText(
          /Si vous souhaitez vous faire rembourser les offres de votre lieu sans SIRET, vous devez sélectionner un lieu avec SIRET dans votre structure/
        )
      ).toBeInTheDocument()

      expect(
        screen.getByText(/ci-dessous le lieu avec SIRET :/)
      ).toBeInTheDocument()

      const select = screen.getByRole('combobox', {
        name: /Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement/,
      })
      expect(select).toBeInTheDocument()

      await userEvent.selectOptions(select, '1')
      await userEvent.click(screen.getByText('Valider la sélection'))

      expect(screen.getByText(/ce lieu avec SIRET/)).toBeInTheDocument()
    })
    it('should display the right wording with the OA FF', async () => {
      renderPricingPoints(defaultProps, {
        features: ['WIP_ENABLE_OFFER_ADDRESS'],
      })

      expect(
        screen.getByText('Sélectionner une structure dans la liste')
      ).toBeInTheDocument()

      expect(
        screen.getByText(
          'Comment ajouter vos coordonnées bancaires sur une structure sans SIRET ?'
        )
      ).toBeInTheDocument()

      expect(
        screen.getByText(
          /Si vous souhaitez vous faire rembourser les offres de votre structure sans SIRET, vous devez sélectionner une structure avec SIRET dans votre entité/
        )
      ).toBeInTheDocument()

      expect(
        screen.getByText(/ci-dessous la structure avec SIRET :/)
      ).toBeInTheDocument()

      const select = screen.getByRole('combobox', {
        name: /Structure avec SIRET utilisée pour le calcul de votre barème de remboursement/,
      })
      expect(select).toBeInTheDocument()

      await userEvent.selectOptions(select, '1')
      await userEvent.click(screen.getByText('Valider la sélection'))

      expect(screen.getByText(/cette structure avec SIRET/)).toBeInTheDocument()
    })
  })
})
