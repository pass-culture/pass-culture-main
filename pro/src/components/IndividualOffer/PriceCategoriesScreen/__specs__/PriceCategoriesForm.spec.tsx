import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'

import { api } from '@/apiClient//api'
import {
  GetIndividualOfferResponseModel,
  GetIndividualOfferWithAddressResponseModel,
} from '@/apiClient//v1'
import { IndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  priceCategoryFactory,
  subcategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { PriceCategoriesScreen } from '@/components/IndividualOffer/PriceCategoriesScreen/PriceCategoriesScreen'

const renderPriceCategoriesForm = (
  canBeDuo = true,
  customGetIndividualOffer?: Partial<GetIndividualOfferWithAddressResponseModel>
) => {
  const offer = getIndividualOfferFactory({
    id: 42,
    hasStocks: false,
    priceCategories: [
      priceCategoryFactory(),
      priceCategoryFactory(),
      priceCategoryFactory(),
    ],
    ...customGetIndividualOffer,
  })
  let context = {
    offer,
    categories: [],
    subCategories: [subcategoryFactory({ id: offer.subcategoryId, canBeDuo })],
    isEvent: null,
    setIsEvent: () => {},
  }
  return renderWithProviders(
    <IndividualOfferContext.Provider value={context}>
      <PriceCategoriesScreen offer={offer} />
    </IndividualOfferContext.Provider>,
    { initialRouterEntries: ['/creation'] }
  )
}

describe('PriceCategories', () => {
  beforeEach(() => {
    vi.spyOn(api, 'postPriceCategories').mockResolvedValue(
      {} as GetIndividualOfferResponseModel
    )
    vi.spyOn(api, 'getOffer').mockResolvedValue(getIndividualOfferFactory())
  })

  it('should render without error', () => {
    renderPriceCategoriesForm()

    expect(screen.getAllByText('Intitulé du tarif')).toHaveLength(3)
    expect(screen.getByText('Réservations “Duo”')).toBeInTheDocument()
  })

  it('should not suggest duo choice when offer cannot be duo', () => {
    renderPriceCategoriesForm(false)

    expect(screen.queryByText('Réservations “Duo”')).not.toBeInTheDocument()
  })

  it('should set tarif to 0 when clicking on free checkbox and vice versa', async () => {
    const values = {
      priceCategories: [
        priceCategoryFactory(),
        priceCategoryFactory(),
        priceCategoryFactory({ price: 0 }),
      ],
      isDuo: false,
    }

    renderPriceCategoriesForm(true, values)

    const freeCheckboxes = screen.getAllByLabelText('Gratuit')

    // I check initial values
    expect(freeCheckboxes[0]).not.toBeChecked()
    expect(freeCheckboxes[1]).not.toBeChecked()
    expect(freeCheckboxes[2]).toBeChecked()

    // I checked all checkboxes are checked
    await userEvent.click(freeCheckboxes[0])
    await userEvent.click(freeCheckboxes[1])

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
    await userEvent.type(tarifFields[2], '0,1')

    expect(freeCheckboxes[0]).not.toBeChecked()
    expect(freeCheckboxes[1]).not.toBeChecked()
    expect(freeCheckboxes[2]).not.toBeChecked()
  })

  it('should remove price categories on trash button click', async () => {
    vi.spyOn(api, 'deletePriceCategory').mockResolvedValue()

    renderPriceCategoriesForm(false, {
      priceCategories: [],
    })

    await userEvent.type(screen.getByLabelText('Prix par personne'), '66.7')
    await userEvent.click(screen.getByText('Ajouter un tarif'))

    await userEvent.type(
      screen.getAllByLabelText('Prix par personne')[1],
      '666.7'
    )
    await userEvent.click(screen.getByText('Ajouter un tarif'))

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
    const values = {
      priceCategories: [
        priceCategoryFactory({ id: 66 }),
        priceCategoryFactory({ id: 2 }),
      ],
      isDuo: true,
    }

    renderPriceCategoriesForm(true, values)

    expect(
      screen.getByLabelText(/Accepter les réservations “Duo“/)
    ).toBeChecked()
    await userEvent.click(
      screen.getByLabelText(/Accepter les réservations “Duo“/)
    )
    expect(
      screen.getByLabelText(/Accepter les réservations “Duo“/)
    ).not.toBeChecked()

    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[0]
    )
    expect(api.deletePriceCategory).toHaveBeenNthCalledWith(1, 42, 66)
    expect(api.postPriceCategories).toHaveBeenNthCalledWith(1, 42, {
      priceCategories: [{ id: 2, label: 'Tarif unique' }],
    })
    expect(
      screen.getByLabelText(/Accepter les réservations “Duo“/)
    ).not.toBeChecked()
  })

  it('should display delete banner when stock is linked and delete right line', async () => {
    vi.spyOn(api, 'deletePriceCategory').mockResolvedValue()
    const values = {
      priceCategories: [
        priceCategoryFactory({ id: 2 }),
        priceCategoryFactory({ id: 144 }),
      ],
      isDuo: false,
      id: 42,
      hasStocks: true,
    }

    renderPriceCategoriesForm(false, values)

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
    await userEvent.click(screen.getByText('Confirmer la suppression'))
    expect(api.deletePriceCategory).toHaveBeenNthCalledWith(1, 42, 144)
  })

  it('should be able to delete the first price category when it has stocks', async () => {
    vi.spyOn(api, 'deletePriceCategory').mockResolvedValue()
    const values = {
      priceCategories: [
        priceCategoryFactory({ id: 2 }),
        priceCategoryFactory({ id: 144 }),
      ],
      isDuo: false,
      id: 42,
      hasStocks: true,
    }

    renderPriceCategoriesForm(true, values)

    // I can cancel
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[0]
    )
    expect(
      screen.getByText(
        'En supprimant ce tarif vous allez aussi supprimer l’ensemble des dates qui lui sont associées.'
      )
    ).toBeInTheDocument()

    await userEvent.click(screen.getByText('Confirmer la suppression'))
    expect(api.deletePriceCategory).toHaveBeenCalledWith(42, 2)
  })

  it('should handle unique line label cases', async () => {
    renderPriceCategoriesForm(true, {
      priceCategories: [],
    })

    // one price category line : label is default and field is disable
    expect(screen.getByTestId('delete-button')).toBeDisabled()
    expect(screen.getByDisplayValue('Tarif unique')).toBeDisabled()
    const nameFields = screen.getAllByLabelText('Intitulé du tarif')
    const priceFields = screen.getAllByLabelText('Prix par personne')
    await userEvent.type(priceFields[0], '66.7')

    // I add a price category line
    await userEvent.click(screen.getByText('Ajouter un tarif'))

    expect(nameFields[0]).toHaveValue('')
    expect(priceFields[0]).toHaveValue(66.7)
    expect(nameFields[0]).not.toBeDisabled()

    // I change the label and remove last line, label is default and field disable
    await userEvent.type(nameFields[0], 'Tarif Koala')
    await userEvent.click(
      screen.getAllByRole('button', { name: 'Supprimer le tarif' })[1]
    )
    // it keep the input price
    expect(priceFields[0]).toHaveValue(66.7)

    expect(nameFields[0]).toBeDisabled()
  })
})
