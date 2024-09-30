import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { FormikProvider, useFormik } from 'formik'

import { api } from 'apiClient/api'
import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { subcategoryFactory } from 'utils/individualApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { sharedCurrentUserFactory } from 'utils/storeFactories'

import { DEFAULT_DETAILS_FORM_VALUES } from '../constants'

import { DetailsEanSearch, DetailsEanSearchProps } from './DetailsEanSearch'

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
  isEvent: null,
  setIsEvent: vi.fn(),
}

const LABELS = {
  eanSearchInput: /Scanner ou rechercher un produit par EAN/,
  eanSearchButton: /Rechercher/,
}

type DetailsEanSearchTestProps = Partial<DetailsEanSearchProps> & {
  wasEanSearchPerformed?: boolean
}

const EanSearchWrappedWithFormik = ({
  isDirtyDraftOffer = false,
  wasEanSearchPerformed = false,
  productId = DEFAULT_DETAILS_FORM_VALUES.productId,
  subcategoryId = DEFAULT_DETAILS_FORM_VALUES.subcategoryId,
  ean = DEFAULT_DETAILS_FORM_VALUES.ean,
  onEanSearch = vi.fn(),
  resetForm = vi.fn(),
}: DetailsEanSearchTestProps): JSX.Element => {
  const formik = useFormik({
    initialValues: {
      ...DEFAULT_DETAILS_FORM_VALUES,
      subcategoryId,
    },
    onSubmit: vi.fn(),
  })

  const hasCompleteValues = !isDirtyDraftOffer || wasEanSearchPerformed
  const mockedSubCategoryId = hasCompleteValues
    ? 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE'
    : subcategoryId
  const mockedProductId = hasCompleteValues ? '0000' : productId
  const mockedEan = hasCompleteValues ? '9781234567897' : ean

  return (
    <FormikProvider value={formik}>
      <DetailsEanSearch
        isDirtyDraftOffer={isDirtyDraftOffer}
        productId={mockedProductId}
        subcategoryId={mockedSubCategoryId}
        ean={mockedEan}
        onEanSearch={onEanSearch}
        resetForm={resetForm}
      />
    </FormikProvider>
  )
}

const renderDetailsEanSearch = (props: DetailsEanSearchTestProps = {}) => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <EanSearchWrappedWithFormik {...props} />
    </IndividualOfferContext.Provider>,
    {
      storeOverrides: {
        user: {
          currentUser: sharedCurrentUserFactory(),
          selectedOffererId: 1,
        },
      },
    }
  )
}

vi.mock('apiClient/api', () => ({
  api: { getProductByEan: vi.fn() },
}))

const successMessage = /Les informations suivantes ont été synchronisées/
const infoMessage = /Les informations de cette page ne sont pas modifiables/
const errorMessage = /Une erreur est survenue lors de la recherche/
const formatErrorMessage = /doit être composé de 13 chiffres/
const subCatErrorMessage = /doivent être liées à un produit/
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
  it('should display an input and a submit button within a dedicated form', () => {
    renderDetailsEanSearch()

    const input = getInput()
    const button = getButton()

    expect(input).toBeInTheDocument()
    expect(button).toBeInTheDocument()
    expect(button).toHaveAttribute('type', 'submit')
  })

  describe('when the draft offer has not been created yet (dirty)', () => {
    describe('when no EAN search has been performed', () => {
      it('should call the ean search API when the form is submitted', async () => {
        const onEanSearch = vi.fn()
        renderDetailsEanSearch({ isDirtyDraftOffer: true, onEanSearch })

        await userEvent.type(getInput(), '9781234567897')
        await userEvent.click(getButton())

        expect(api.getProductByEan).toHaveBeenCalledWith('9781234567897', 1)
        expect(onEanSearch.mock.calls.length).toBe(1)
      })

      describe('when the input has format issues', () => {
        it('should display an error message', async () => {
          renderDetailsEanSearch({ isDirtyDraftOffer: true })

          await userEvent.type(getInput(), '123')
          await userEvent.tab()

          expect(getInput()).toBeInvalid()
          expect(screen.getByRole('alert')).toHaveTextContent(
            formatErrorMessage
          )
        })

        it('should disable the submit button', async () => {
          renderDetailsEanSearch({ isDirtyDraftOffer: true })

          expect(getButton()).toBeDisabled()
          await userEvent.type(getInput(), '123')
          expect(getButton()).toBeDisabled()
        })
      })

      describe('when the subcategory requires an EAN', () => {
        it('should display a (cumulative) error message that cannot be cleared on new inputs', async () => {
          renderDetailsEanSearch({
            isDirtyDraftOffer: true,
            subcategoryId: 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE',
          })

          // Input is now required.
          const eanInput = getInput()
          expect(eanInput).toBeRequired()

          // Error cannot be removed by typing in the input.
          expect(screen.getByText(subCatErrorMessage)).toBeInTheDocument()
          await userEvent.type(eanInput, '9781234567897')
          expect(screen.getByText(subCatErrorMessage)).toBeInTheDocument()
        })

        it('should let the submit button enabled', async () => {
          renderDetailsEanSearch({
            isDirtyDraftOffer: true,
            subcategoryId: 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE',
          })

          await userEvent.type(getInput(), '9781234567897')
          expect(getButton()).not.toBeDisabled()
        })
      })
    })

    describe('when an EAN search is performed succesfully', () => {
      it('should display a success message', () => {
        renderDetailsEanSearch({
          isDirtyDraftOffer: true,
          wasEanSearchPerformed: true,
        })

        const status = screen.getAllByRole('status')
        expect(
          status.some(
            (s) => s.textContent && successMessage.test(s.textContent)
          )
        ).toBe(true)
      })

      it('should be entirely disabled', () => {
        renderDetailsEanSearch({
          isDirtyDraftOffer: true,
          wasEanSearchPerformed: true,
        })

        expect(getInput()).toBeDisabled()
        expect(getButton()).toBeDisabled()
      })

      it('should clear the form when the clear button is clicked', async () => {
        const resetForm = vi.fn()
        renderDetailsEanSearch({
          isDirtyDraftOffer: true,
          wasEanSearchPerformed: true,
          resetForm,
        })

        const clearButton = screen.getByRole('button', {
          name: clearButtonLabel,
        })

        expect(clearButton).toBeInTheDocument()

        await userEvent.click(clearButton)
        expect(resetForm.mock.calls.length).toBe(1)
      })
    })

    describe('when an EAN search is performed and ends with an error', () => {
      it('should display an error message', async () => {
        vi.spyOn(api, 'getProductByEan').mockRejectedValue(new Error('error'))
        renderDetailsEanSearch({ isDirtyDraftOffer: true })

        expect(screen.queryByText(errorMessage)).not.toBeInTheDocument()

        await userEvent.type(getInput(), '9781234567897')
        await userEvent.click(getButton())

        expect(screen.queryByText(errorMessage)).toBeInTheDocument()
      })

      it('should disable the submit button', async () => {
        vi.spyOn(api, 'getProductByEan').mockRejectedValue(new Error('error'))
        renderDetailsEanSearch({ isDirtyDraftOffer: true })

        await userEvent.type(getInput(), '9781234567897')
        await userEvent.click(getButton())

        expect(getButton()).toBeDisabled()
      })
    })
  })

  describe('when the draft offer has been created and the offer is product-based', () => {
    it('should not display the clear button anymore', () => {
      renderDetailsEanSearch({
        isDirtyDraftOffer: false,
        wasEanSearchPerformed: true,
      })

      expect(
        screen.queryByRole('button', {
          name: clearButtonLabel,
        })
      ).not.toBeInTheDocument()
    })

    it('should display an info message', () => {
      renderDetailsEanSearch({
        isDirtyDraftOffer: false,
        wasEanSearchPerformed: true,
      })

      expect(screen.queryByText(infoMessage)).toBeInTheDocument()
    })
  })
})
