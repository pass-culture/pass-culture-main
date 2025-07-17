import {
  screen,
  waitFor,
  waitForElementToBeRemoved,
} from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { api } from 'apiClient/api'
import {
  GetIndividualOfferWithAddressResponseModel,
  GetOfferStockResponseModel,
} from 'apiClient/v1'
import { IndividualOfferContextProvider } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferUrl } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import {
  getIndividualOfferFactory,
  listOffersOfferFactory,
} from 'commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from 'commons/utils/factories/storeFactories'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'

import { PRICE_CATEGORY_MAX_LENGTH } from './form/constants'
import { PriceCategoriesScreen } from './PriceCategoriesScreen'

const renderPriceCategoriesScreen = async (
  apiOffer: GetIndividualOfferWithAddressResponseModel,
  apiStocks: GetOfferStockResponseModel[] = [],
  stocksCount?: number
) => {
  vi.spyOn(api, 'getOffer').mockResolvedValue(apiOffer)
  vi.spyOn(api, 'getCategories').mockResolvedValue({
    categories: [],
    subcategories: [],
  })
  vi.spyOn(api, 'getVenues').mockResolvedValue({ venues: [] })
  vi.spyOn(api, 'listOfferersNames').mockResolvedValue({ offerersNames: [] })
  vi.spyOn(api, 'getStocks').mockResolvedValue({
    stocks: apiStocks,
    stockCount: stocksCount ?? apiStocks.length,
    hasStocks: true,
  })
  vi.spyOn(api, 'listOffers').mockResolvedValue([listOffersOfferFactory()])

  renderWithProviders(
    <IndividualOfferContextProvider>
      <PriceCategoriesScreen offer={apiOffer} />
    </IndividualOfferContextProvider>,
    {
      user: sharedCurrentUserFactory(),
      initialRouterEntries: [
        getIndividualOfferUrl({
          step: OFFER_WIZARD_STEP_IDS.TARIFS,
          mode: OFFER_WIZARD_MODE.CREATION,
          offerId: apiOffer.id,
        }),
      ],
    }
  )

  await waitForElementToBeRemoved(() => screen.queryAllByTestId('spinner'))
}

describe('PriceCategoriesScreen', () => {
  let apiOffer: GetIndividualOfferWithAddressResponseModel

  beforeEach(() => {
    apiOffer = getIndividualOfferFactory()
  })

  it('shows validation errors on submit if required fields are empty', async () => {
    await renderPriceCategoriesScreen(apiOffer)

    await userEvent.click(screen.getByText(/ajouter un tarif/i))

    await userEvent.tab()

    expect(
      screen.getByText('Veuillez renseigner un intitulé de tarif')
    ).toBeInTheDocument()
  })

  it('clears errors when fields are filled', async () => {
    await renderPriceCategoriesScreen(apiOffer)

    await userEvent.click(screen.getByText(/ajouter un tarif/i))

    const labelInput = screen.getAllByLabelText('Intitulé du tarif')
    const priceInput = screen.getAllByLabelText('Prix par personne')

    await userEvent.clear(labelInput[1])
    await userEvent.type(labelInput[1], 'Plein tarif')

    await userEvent.clear(priceInput[1])
    await userEvent.type(priceInput[1], '20')

    await waitFor(() => {
      expect(
        screen.queryByText('Veuillez renseigner un intitulé de tarif')
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText('Veuillez renseigner un tarif')
      ).not.toBeInTheDocument()
    })
  })

  it('shows error when price is too high', async () => {
    await renderPriceCategoriesScreen(apiOffer)

    await userEvent.click(screen.getByText(/ajouter un tarif/i))
    const priceInput = screen.getAllByLabelText('Prix par personne')

    await userEvent.clear(priceInput[0])
    await userEvent.type(priceInput[0], '1000')

    await waitFor(() => {
      expect(
        screen.getByText(/Veuillez renseigner un tarif inférieur à/)
      ).toBeInTheDocument()
    })
  })

  it('deletes a price category when clicking delete', async () => {
    await renderPriceCategoriesScreen(apiOffer)

    await userEvent.click(screen.getByText(/ajouter un tarif/i))
    expect(screen.getByTestId('priceCategories.1.label')).toBeInTheDocument()

    const deleteButtons = screen.getAllByTestId('delete-button')

    await userEvent.click(deleteButtons[1])

    await waitFor(() => {
      expect(
        screen.queryByTestId('priceCategories.1.label')
      ).not.toBeInTheDocument()
    })
  })

  it('adds a new price category when clicking add', async () => {
    await renderPriceCategoriesScreen(apiOffer)

    await userEvent.click(screen.getByText(/ajouter un tarif/i))
    await userEvent.click(screen.getByText(/ajouter un tarif/i))

    expect(screen.getAllByLabelText('Intitulé du tarif').length).toBe(3)
  })

  it('toggles Duo checkbox', async () => {
    await renderPriceCategoriesScreen(apiOffer)

    const checkbox = screen.getByRole('checkbox')
    expect(checkbox).not.toBeChecked()

    await userEvent.click(checkbox)
    expect(checkbox).toBeChecked()
  })

  it('should not be possible to edit tarif label if we have only one tarif', async () => {
    await renderPriceCategoriesScreen(apiOffer)

    expect(screen.getByTestId('priceCategories.0.label')).toBeInTheDocument()

    const deleteButtons = screen.getAllByTestId('delete-button')
    expect(deleteButtons[0]).toBeDisabled()

    const priceLabel = screen.getByRole('textbox', {
      name: 'Intitulé du tarif',
    })
    expect(priceLabel).toBeDisabled()
    expect(priceLabel).toHaveValue('mon label')
  })

  it('disables "Ajouter un tarif" button when reaching max number of categories', async () => {
    await renderPriceCategoriesScreen(apiOffer)

    for (let i = 0; i < PRICE_CATEGORY_MAX_LENGTH - 1; i++) {
      await userEvent.click(screen.getByText(/ajouter un tarif/i))
    }

    expect(screen.getByText(/ajouter un tarif/i)).toBeDisabled()
  })

  it('submits form when confirmation modal is accepted', async () => {
    const spySubmit = vi
      .spyOn(api, 'postPriceCategories')
      .mockResolvedValue(apiOffer)

    const offerWithStocks = {
      ...apiOffer,
      hasStocks: true,
      priceCategories: [
        {
          id: 1,
          label: 'Old',
          price: 100,
        },
      ],
    }

    await renderPriceCategoriesScreen(offerWithStocks)

    const priceInput = screen.getAllByLabelText('Prix par personne')
    await userEvent.clear(priceInput[0])
    await userEvent.type(priceInput[0], '300')

    await userEvent.click(
      screen.getByRole('button', { name: /Enregistrer et continuer/i })
    )

    expect(
      screen.getByText(/modification de tarif s’appliquera/i)
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Confirmer la modification'))

    await waitFor(() => {
      expect(spySubmit).toHaveBeenCalledOnce()
    })
  })

  it('shows confirmation dialog before deleting a saved price category with stocks', async () => {
    const modifiedApiOffer = {
      ...apiOffer,
      hasStocks: true,
      priceCategories: [
        {
          id: 1,
          label: 'first',
          price: 100,
        },
        {
          id: 2,
          label: 'second',
          price: 50,
        },
      ],
    }

    await renderPriceCategoriesScreen(modifiedApiOffer)

    const deleteButton = screen.getAllByTestId('delete-button')
    await userEvent.click(deleteButton[1])

    expect(
      screen.getByText(/vous allez aussi supprimer l’ensemble des dates/i)
    ).toBeInTheDocument()
  })
})
