import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { axe } from 'vitest-axe'

import { api } from '@/apiClient/api'
import { VenueState } from '@/apiClient/v1'
import {
  IndividualOfferContext,
  type IndividualOfferContextValues,
} from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { subcategoryFactory } from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { makeGetVenueResponseModel } from '@/commons/utils/factories/venueFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  DetailsEanSearch,
  type DetailsEanSearchProps,
} from './DetailsEanSearch'

const contextValue: IndividualOfferContextValues = {
  categories: [],
  subCategories: [
    subcategoryFactory({
      id: 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE',
      categoryId: 'MUSIQUE_ENREGISTREE',
      proLabel: 'Vinyles et autres supports',
      conditionalFields: ['gtl_id', 'author', 'performer', 'ean'],
    }),
  ],
  offer: null,
  offerId: null,
  isEvent: null,
  setIsControlledEvent: vi.fn(),
  hasPublishedOfferWithSameEan: false,
}

const LABELS = {
  eanSearchInput: /Scanner ou rechercher un produit par EAN/,
  eanSearchButton: /Rechercher/,
}

const renderDetailsEanSearch = (props: Partial<DetailsEanSearchProps> = {}) => {
  const {
    canClearProduct = false,
    productEan = '',
    required = false,
    disabled = false,
    onProductChange = vi.fn(),
  } = props

  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <DetailsEanSearch
        canClearProduct={canClearProduct}
        productEan={productEan}
        required={required}
        disabled={disabled}
        onProductChange={onProductChange}
      />
    </IndividualOfferContext.Provider>,
    {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedPartnerVenue: makeGetVenueResponseModel({ id: 2 }),
        },
      },
    }
  )
}

vi.mock('@/apiClient/api', () => ({
  api: { getProductByEan: vi.fn() },
}))

const errorMessage = /Une erreur est survenue lors de la recherche/
const formatErrorMessage = /doit être composé de 13 chiffres/
const clearButtonLabel = /Effacer/

const getInput = () =>
  screen.getByRole('textbox', {
    name: LABELS.eanSearchInput,
  })

const getButton = () =>
  screen.getByRole('button', {
    name: LABELS.eanSearchButton,
  })

describe('DetailsEanSearch', () => {
  it('should render without accessibility violations', async () => {
    const { container } = renderDetailsEanSearch()

    await waitFor(() => {
      expect(getInput()).toBeEnabled()
    })

    expect(await axe(container)).toHaveNoViolations()
  })

  it('should display an input and a submit button within a dedicated form', async () => {
    renderDetailsEanSearch()

    const input = getInput()
    const button = getButton()

    await waitFor(() => {
      expect(input).toBeInTheDocument()
      expect(button).toBeInTheDocument()
      expect(button).toHaveAttribute('type', 'submit')
    })
  })

  describe('when the draft offer has not been created yet (dirty)', () => {
    describe('when no EAN search has been performed', () => {
      it('should call the ean search API when the form is submitted', async () => {
        const onProductChange = vi.fn()
        renderDetailsEanSearch({ canClearProduct: true, onProductChange })

        await userEvent.type(getInput(), '9781234567897')
        await userEvent.click(getButton())

        expect(api.getProductByEan).toHaveBeenCalledWith({
          path: {
            ean: '9781234567897',
            offerer_id: 1,
          },
        })
        expect(onProductChange).toHaveBeenCalledTimes(1)
      })

      describe('when the input has format issues', () => {
        it('should display an error message', async () => {
          renderDetailsEanSearch({ canClearProduct: true })

          await userEvent.type(getInput(), '123')
          await userEvent.tab()

          expect(getInput()).toBeInvalid()
          expect(screen.getByRole('alert')).toHaveTextContent(
            formatErrorMessage
          )
        })

        it('should disable the submit button', async () => {
          renderDetailsEanSearch({ canClearProduct: true })

          expect(getButton()).toBeDisabled()
          await userEvent.type(getInput(), '123')
          expect(getButton()).toBeDisabled()
        })
      })
    })

    describe('when the subcategory requires an EAN', () => {
      it('should display a (cumulative) error message that cannot be cleared on new inputs', async () => {
        renderDetailsEanSearch({
          canClearProduct: true,
          required: true,
        })

        // Input is now required.
        const eanInput = getInput()
        expect(eanInput).toBeRequired()

        // The required error is shown as soon as the field is touched.
        expect(
          await screen.findByText(/doivent être liées à un produit/)
        ).toBeInTheDocument()

        // Error cannot be removed by typing in the input.
        await userEvent.type(eanInput, '9781234567897')
        expect(
          screen.getByText(/doivent être liées à un produit/)
        ).toBeInTheDocument()
      })

      it('should let the submit button enabled', async () => {
        renderDetailsEanSearch({
          canClearProduct: true,
          required: true,
        })

        await userEvent.type(getInput(), '9781234567897')
        expect(getButton()).not.toBeDisabled()
      })
    })

    describe('when an EAN search is performed succesfully', () => {
      it('should display a success message', async () => {
        const successMessage =
          /Ces informations ont été récupérées depuis l’EAN./

        renderDetailsEanSearch({
          canClearProduct: true,
          productEan: '9781234567897',
        })

        await waitFor(() => {
          const status = screen.getAllByRole('status')
          expect(
            status.some(
              (s) => s.textContent && successMessage.test(s.textContent)
            )
          ).toBe(true)
        })
      })

      it('should be entirely disabled', async () => {
        renderDetailsEanSearch({
          disabled: true,
        })

        await waitFor(() => {
          expect(getInput()).toBeDisabled()
          expect(getButton()).toBeDisabled()
        })
      })

      it.skip('should display an error message if POST API ends with an EAN error', async () => {
        // Should not be tested here
        // but the feature is already broken on master

        const eanSubmitError = 'This EAN is already used'
        renderDetailsEanSearch({
          canClearProduct: true,
          productEan: '9781234567897',
        })

        await waitFor(() => {
          expect(screen.queryByText(eanSubmitError)).toBeInTheDocument()
        })
      })
    })

    describe('when an EAN search is performed and ends with a product API error', () => {
      it('should display an error message', async () => {
        vi.spyOn(api, 'getProductByEan').mockRejectedValue(new Error('error'))
        renderDetailsEanSearch({ canClearProduct: true })

        expect(screen.queryByText(errorMessage)).not.toBeInTheDocument()

        await userEvent.type(getInput(), '9781234567897')
        await userEvent.click(getButton())

        expect(screen.getByText(errorMessage)).toBeInTheDocument()
      })

      it('should disable the submit button', async () => {
        vi.spyOn(api, 'getProductByEan').mockRejectedValue(new Error('error'))
        renderDetailsEanSearch({ canClearProduct: true })

        await userEvent.type(getInput(), '9781234567897')
        await userEvent.click(getButton())

        expect(getButton()).toBeDisabled()
      })
    })
  })

  it('should disable the input when the selected partner venue is closed', async () => {
    renderWithProviders(
      <IndividualOfferContext.Provider value={contextValue}>
        <DetailsEanSearch
          canClearProduct={true}
          onProductChange={vi.fn()}
          required={true}
          disabled={true}
          productEan={undefined}
        />
      </IndividualOfferContext.Provider>,
      {
        storeOverrides: {
          user: {
            currentUser: sharedCurrentUserFactory(),
            selectedPartnerVenue: makeGetVenueResponseModel({
              id: 2,
              state: VenueState.CLOSED,
            }),
          },
        },
      }
    )

    await waitFor(() => {
      expect(getInput()).toBeDisabled()
    })
  })

  describe('when the draft offer has been created and the offer is product-based', () => {
    const productEan = '9781234567897'

    it('should init the input with the offer EAN', async () => {
      renderDetailsEanSearch({
        canClearProduct: false,
        productEan,
      })

      await waitFor(() => {
        expect(getInput()).toHaveValue(productEan)
      })
    })

    it('should not display the clear button anymore', async () => {
      renderDetailsEanSearch({
        canClearProduct: false,
        productEan,
      })

      await waitFor(() => {
        expect(
          screen.queryByRole('button', {
            name: clearButtonLabel,
          })
        ).not.toBeInTheDocument()
      })
    })
  })
})
