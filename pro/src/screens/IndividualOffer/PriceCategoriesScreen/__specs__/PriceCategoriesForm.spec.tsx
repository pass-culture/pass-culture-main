import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'

import { api } from 'apiClient/api'
import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { OFFER_WIZARD_MODE } from 'core/Offers/constants'
import { GetIndividualOfferFactory } from 'utils/apiFactories'
import { individualOfferFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import {
  FIRST_INITIAL_PRICE_CATEGORY,
  PRICE_CATEGORY_MAX_LENGTH,
} from '../form/constants'
import { priceCategoryFormFactory } from '../form/factories'
import { PriceCategoriesFormValues } from '../form/types'
import {
  PriceCategoriesForm,
  PriceCategoriesFormProps,
} from '../PriceCategoriesForm'

const defaultValues: PriceCategoriesFormValues = {
  priceCategories: [
    priceCategoryFormFactory(),
    priceCategoryFormFactory(),
    priceCategoryFormFactory(),
  ],
  isDuo: false,
}

const renderPriceCategoriesForm = (
  customValues?: Partial<PriceCategoriesFormValues>,
  customProps?: Partial<PriceCategoriesFormProps>
) => {
  const values = { ...defaultValues, ...customValues }
  return renderWithProviders(
    <Formik initialValues={values} onSubmit={vi.fn()}>
      <PriceCategoriesForm
        offer={individualOfferFactory({ id: 42, hasStocks: false })}
        mode={OFFER_WIZARD_MODE.CREATION}
        setOffer={vi.fn()}
        isDisabled={false}
        {...customProps}
      />
    </Formik>
  )
}

describe('PriceCategories', () => {
  beforeEach(() => {
    vi.spyOn(api, 'postPriceCategories').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'getOffer').mockResolvedValue(GetIndividualOfferFactory())
  })

  it('should render without error', () => {
    renderPriceCategoriesForm(undefined, { canBeDuo: true })

    expect(screen.getAllByText('Intitulé du tarif')).toHaveLength(3)
    expect(screen.getByText('Réservations “Duo”')).toBeInTheDocument()
  })

  it('should not suggest duo choice when offer cannot be duo', () => {
    renderPriceCategoriesForm(undefined, { canBeDuo: false })

    expect(screen.queryByText('Réservations “Duo”')).not.toBeInTheDocument()
  })

  it('should set tarif to 0 when clicking on free checkbox and vice versa', async () => {
    const values: PriceCategoriesFormValues = {
      priceCategories: [
        priceCategoryFormFactory(),
        priceCategoryFormFactory({ price: 0 }),
        priceCategoryFormFactory(),
      ],
      isDuo: false,
    }

    renderPriceCategoriesForm(values)

    const freeCheckboxes = screen.getAllByLabelText('Gratuit')

    // I check initial values
    expect(freeCheckboxes[0]).not.toBeChecked()
    expect(freeCheckboxes[1]).toBeChecked()
    expect(freeCheckboxes[2]).not.toBeChecked()

    // I checked all checkboxes are checked
    await userEvent.click(freeCheckboxes[0])
    await userEvent.click(freeCheckboxes[2])

    expect(freeCheckboxes[0]).toBeChecked()
    expect(freeCheckboxes[1]).toBeChecked()
    expect(freeCheckboxes[2]).toBeChecked()

    const tarifFields = screen.getAllByLabelText('Prix par personne')
    expect(tarifFields[0]).toHaveValue(0)
    expect(tarifFields[1]).toHaveValue(0)
    expect(tarifFields[2]).toHaveValue(0)

    // I set prices checkboxes are unchecked
    await userEvent.type(tarifFields[0], '20')
    await userEvent.type(tarifFields[1], '21')
    await userEvent.type(tarifFields[2], '0.1')

    expect(freeCheckboxes[0]).not.toBeChecked()
    expect(freeCheckboxes[1]).not.toBeChecked()
    expect(freeCheckboxes[2]).not.toBeChecked()
  })

  it('should not let add more than 20 price categories', async () => {
    renderPriceCategoriesForm({ priceCategories: [priceCategoryFormFactory()] })

    for (let i = 0; i < PRICE_CATEGORY_MAX_LENGTH - 1; i++) {
      await userEvent.click(screen.getByText('Ajouter un tarif'))
    }

    expect(screen.getAllByText('Intitulé du tarif')).toHaveLength(
      PRICE_CATEGORY_MAX_LENGTH
    )
    expect(screen.getByText('Ajouter un tarif')).toBeDisabled()
  })

  it('should remove price categories on trash button click', async () => {
    vi.spyOn(api, 'deletePriceCategory').mockResolvedValue()

    renderPriceCategoriesForm()

    expect(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[0]
    ).toBeEnabled()
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[0]
    )
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[0]
    )
    expect(screen.getAllByTestId('delete-button')[0]).toBeDisabled()

    expect(api.deletePriceCategory).not.toHaveBeenCalled()
  })

  it('should remove price categories on trash button click and rename last one', async () => {
    vi.spyOn(api, 'deletePriceCategory').mockResolvedValue()
    const values: PriceCategoriesFormValues = {
      priceCategories: [
        priceCategoryFormFactory({ id: 66 }),
        priceCategoryFormFactory({ id: 2 }),
      ],
      isDuo: true,
    }

    renderPriceCategoriesForm(values, { canBeDuo: true })
    await userEvent.click(
      screen.getByLabelText('Accepter les réservations “Duo“')
    )
    expect(
      screen.getByLabelText('Accepter les réservations “Duo“')
    ).not.toBeChecked()

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[0]
    )
    expect(api.deletePriceCategory).toHaveBeenNthCalledWith(1, 42, 66)
    expect(api.postPriceCategories).toHaveBeenNthCalledWith(1, 42, {
      priceCategories: [{ id: 2, label: 'Tarif unique' }],
    })
    expect(
      screen.getByLabelText('Accepter les réservations “Duo“')
    ).not.toBeChecked()
  })

  it('should display delete banner when stock is linked and delete right line', async () => {
    vi.spyOn(api, 'deletePriceCategory').mockResolvedValue()
    const values: PriceCategoriesFormValues = {
      priceCategories: [
        priceCategoryFormFactory({ id: 2 }),
        priceCategoryFormFactory({ id: 144 }),
      ],
      isDuo: false,
    }

    renderPriceCategoriesForm(values, {
      offer: individualOfferFactory({ id: 42, hasStocks: true }),
    })

    // I can cancel
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[1]
    )
    expect(
      screen.getByText(
        'En supprimant ce tarif vous allez aussi supprimer l’ensemble des dates qui lui sont associées.'
      )
    ).toBeInTheDocument()
    await userEvent.click(screen.getByText('Annuler'))
    expect(api.deletePriceCategory).not.toHaveBeenCalled()

    // I can delete
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[1]
    )
    await userEvent.click(screen.getByText('Confirmer la supression'))
    expect(api.deletePriceCategory).toHaveBeenNthCalledWith(1, 42, 144)
  })

  it('should handle unique line label cases', async () => {
    renderPriceCategoriesForm({
      priceCategories: [FIRST_INITIAL_PRICE_CATEGORY],
    })

    // one price category line : label is default and field is disable
    expect(screen.getByTestId('delete-button')).toBeDisabled()
    expect(screen.getByDisplayValue('Tarif unique')).toBeDisabled()

    // I add a price category line
    await userEvent.click(screen.getByText('Ajouter un tarif'))
    const nameFields = screen.getAllByLabelText('Intitulé du tarif')
    expect(nameFields[0]).toHaveValue('')
    expect(nameFields[0]).not.toBeDisabled()

    // I change the label and remove last line, label is default and field disable
    await userEvent.type(nameFields[0], 'Tarif Koala')
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[1]
    )
    expect(nameFields[0]).toHaveValue('Tarif unique')
    expect(nameFields[0]).toBeDisabled()
  })
})
