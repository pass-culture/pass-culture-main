import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { configureTestStore } from 'store/testUtils'
import PricingPoint from '../PricingPoint'
import { Form } from 'react-final-form'
import { Provider } from 'react-redux'
import React from 'react'
import userEvent from '@testing-library/user-event'

const renderPricingPointFields = async ({
  props,
  formValues = {},
  storeOverride = {},
}) => {
  const store = configureTestStore(storeOverride)
  const rtlReturns = render(
    <Provider store={store}>
      <Form initialValues={formValues} name="venue" onSubmit={() => null}>
        {() => <PricingPoint {...props} />}
      </Form>
    </Provider>
  )
  await screen.findByText('Barème de remboursement')
  return rtlReturns
}
describe('src | components | pages | Venue | fields | PricingPoint', () => {
  let props
  let formValues
  beforeEach(() => {
    formValues = {
      siret: '12345678912345',
      name: 'Venue name',
      publicName: 'Venue publicName',
      bookingEmail: 'booking@email.app',
      venueTypeCode: 'OTHER_TYPE_ID',
      venueLabelId: 'OTHER_LABEL_ID',
      description: 'Venue description',
    }
    props = {
      ...props,
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
    }
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
      screen.queryByTestId('pricingPointSelect'),
      screen.queryByText(/test - 1000001111/)
    )

    const selectedValued = screen.queryByText(/test - 1000001111/)
    const venueSiretButton = screen.getByRole('button', {
      name: /Valider la sélection/,
      exact: false,
    })

    expect(selectedValued).toBeInTheDocument()
    expect(venueSiretButton).toBeEnabled()
  })

  it.skip('should submit venue pricing point', async () => {
    await renderPricingPointFields({ props, formValues })

    await userEvent.selectOptions(
      screen.queryByTestId('pricingPointSelect'),
      screen.queryByText(/test - 1000001111/)
    )

    const selectedValued = screen.queryByText(/test - 1000001111/)
    const venueSiretButton = await screen.getByRole('button', {
      name: /Valider la sélection/,
      exact: false,
    })

    await userEvent.click(venueSiretButton)

    const validationText = await screen.queryByTestId('validationText')

    expect(selectedValued).toBeInTheDocument()
    expect(validationText).toBeInTheDocument()
  })
})
