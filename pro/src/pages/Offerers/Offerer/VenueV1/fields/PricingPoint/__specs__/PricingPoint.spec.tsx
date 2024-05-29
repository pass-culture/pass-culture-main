import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'

import { api } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { defaultGetVenue } from 'utils/collectiveApiFactories'
import {
  defaultGetOffererVenueResponseModel,
  defaultGetOffererResponseModel,
} from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import { PricingPoint, PricingPointProps } from '../PricingPoint'

vi.mock('apiClient/api', () => ({
  api: {
    linkVenueToPricingPoint: vi.fn(),
  },
}))

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
    renderWithProviders(
      <Formik initialValues={{}} onSubmit={() => {}}>
        <PricingPoint {...defaultProps} />
      </Formik>
    )

    await userEvent.selectOptions(
      screen.getByLabelText(
        'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement *'
      ),
      '0'
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
      'hooks/useNotification'
    )) as ReturnType<typeof useNotification.useNotification>
    vi.spyOn(useNotification, 'useNotification').mockImplementation(() => ({
      ...notifsImport,
      error: mockNotifyError,
    }))
    renderWithProviders(
      <Formik initialValues={{}} onSubmit={() => {}}>
        <PricingPoint {...defaultProps} />
      </Formik>
    )

    await userEvent.selectOptions(
      screen.getByLabelText(
        'Lieu avec SIRET utilisé pour le calcul de votre barème de remboursement *'
      ),
      '0'
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
