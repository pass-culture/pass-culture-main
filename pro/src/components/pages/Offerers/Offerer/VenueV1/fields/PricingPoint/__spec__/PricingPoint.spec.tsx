import '@testing-library/jest-dom'

import PricingPoint, { IPricingPointProps } from '../PricingPoint'
import { render, screen, waitFor } from '@testing-library/react'

import { Form } from 'react-final-form'
import React from 'react'
import { api } from 'apiClient/api'
import userEvent from '@testing-library/user-event'
const renderPricingPointFields = async ({
  props,
  formValues = {},
}: {
  props: IPricingPointProps
  formValues: { venueSiret?: string }
}) => {
  const rtlReturns = render(
    <Form initialValues={formValues} name="venue" onSubmit={async () => null}>
      {() => <PricingPoint {...props} />}
    </Form>
  )
  await screen.findByText('Barème de remboursement')
  return rtlReturns
}
jest.mock('apiClient/api', () => ({
  api: {
    linkVenueToPricingPoint: jest.fn(),
  },
}))
describe('src | components | pages | Venue | fields | PricingPoint', () => {
  let props: IPricingPointProps
  let formValues: { venueSiret?: string }
  beforeEach(() => {
    jest.spyOn(api, 'linkVenueToPricingPoint').mockResolvedValue()
    formValues = {}
    const setVenueHasPricingPoint = jest.fn()
    props = {
      readOnly: false,
      venue: {
        name: 'testName',
        publicName: null,
        id: 'HE',
        managingOffererId: 'DY',
        nonHumanizedId: 57,
        managingOfferer: {
          id: 'DY',
        },
        pricingPoint: null,
        reimbursementPointId: null,
        siret: null,
      },
      offerer: {
        hasAvailablePricingPoints: true,
        managedVenues: [
          {
            id: 'F4',
            managingOffererId: 'DY',
            name: 'test',
            publicName: null,
            siret: 1000001111,
          },
        ],
      },
      setVenueHasPricingPoint: setVenueHasPricingPoint,
    } as unknown as IPricingPointProps
  })

  it('should display component', async () => {
    await renderPricingPointFields({ props, formValues })
    const venueSiretSection = screen.getByText(/Barème de remboursement/)
    const venueSiretSelect = screen.getByText(
      /Sélectionner un lieu dans la liste/
    )

    expect(venueSiretSection).toBeInTheDocument()
    expect(venueSiretSelect).toBeInTheDocument()
  })

  it('should enabled button on select', async () => {
    await renderPricingPointFields({ props, formValues })

    await userEvent.selectOptions(
      screen.getByTestId('pricingPointSelect'),
      screen.getByText(/test - 1000001111/)
    )

    const selectedValued = screen.queryByText(/test - 1000001111/)
    const venueSiretButton = screen.getByRole('button', {
      name: /Valider la sélection/,
      exact: false,
    })

    expect(selectedValued).toBeInTheDocument()
    expect(venueSiretButton).toBeEnabled()
  })

  it('should submit venue pricing point', async () => {
    await renderPricingPointFields({ props, formValues })

    await userEvent.selectOptions(
      screen.getByTestId('pricingPointSelect'),
      screen.getByText(/test - 1000001111/)
    )

    const selectedValued = screen.queryByText(/test - 1000001111/)
    const venueSiretButton = await screen.getByRole('button', {
      name: /Valider la sélection/,
      exact: false,
    })

    await userEvent.click(venueSiretButton)

    const confirmButton = await screen.getByRole('button', {
      name: /Valider ma sélection/,
      exact: false,
    })

    await userEvent.click(confirmButton)

    expect(selectedValued).toBeInTheDocument()

    await waitFor(() => {
      const validationText = screen.queryByTestId('validationText')
      expect(validationText).toBeInTheDocument()
    })
  })
  it('should not display submit button when venue have pricing point', async () => {
    props = {
      ...props,
      venue: {
        pricingPoint: {
          id: 2,
        },
      },
    } as IPricingPointProps
    await renderPricingPointFields({ props, formValues })

    expect(
      screen.queryByText('Valider la sélection', { selector: 'button' })
    ).not.toBeInTheDocument()
  })
})
