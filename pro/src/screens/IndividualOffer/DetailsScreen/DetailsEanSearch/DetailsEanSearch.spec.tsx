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

type RequiredProps = 'isOfferProductBased'
type DetailsEanSearchTestProps = Pick<DetailsEanSearchProps, RequiredProps>

const EanSearchWrappedWithFormik = ({
  props: { isOfferProductBased },
  subcategoryId = DEFAULT_DETAILS_FORM_VALUES.subcategoryId,
}: {
  props: DetailsEanSearchTestProps
  subcategoryId?: string
}): JSX.Element => {
  const formik = useFormik({
    initialValues: {
      ...DEFAULT_DETAILS_FORM_VALUES,
      subcategoryId,
    },
    onSubmit: vi.fn(),
  })

  const setImageOffer: DetailsEanSearchProps['setImageOffer'] = vi.fn()

  return (
    <FormikProvider value={formik}>
      <DetailsEanSearch
        setImageOffer={setImageOffer}
        isOfferProductBased={isOfferProductBased}
      />
    </FormikProvider>
  )
}

const renderDetailsEanSearch = ({
  props,
  subcategoryId = DEFAULT_DETAILS_FORM_VALUES.subcategoryId,
}: {
  props: DetailsEanSearchTestProps
  subcategoryId?: string
}) => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <EanSearchWrappedWithFormik props={props} subcategoryId={subcategoryId} />
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

const buttonLabel = /Rechercher/
const inputLabel = /Scanner ou rechercher un produit par EAN/
const successMessage = /Les informations suivantes ont été synchronisées/
const infoMessage = /Les informations de cette page ne sont pas modifiables/
const errorMessage = /Une erreur est survenue lors de la recherche/
const subCatErrorMessage = /doivent être liées à un produit/
const clearButtonLabel = /Effacer/

describe('DetailsEanSearch', () => {
  describe('before form submission - draft offer has not been created yet', () => {
    describe('when no EAN search has been performed', () => {
      it('should display a permanent error message if the subcategory requires an EAN', async () => {
        renderDetailsEanSearch({
          props: { isOfferProductBased: false },
          subcategoryId: 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE',
        })

        const eanInput = screen.getByRole('textbox', { name: inputLabel })

        // Input is now required.
        expect(eanInput).toBeRequired()

        // Error cannot be removed by typing in the input.
        expect(screen.getByText(subCatErrorMessage)).toBeInTheDocument()
        await userEvent.type(eanInput, '9781234567897')
        expect(screen.getByText(subCatErrorMessage)).toBeInTheDocument()
      })

      it('should let the submit button enabled', async () => {
        renderDetailsEanSearch({ props: { isOfferProductBased: false } })

        const eanInput = screen.getByRole('textbox', { name: inputLabel })
        await userEvent.type(eanInput, '9781234567897')

        const button = screen.getByRole('button', { name: buttonLabel })
        expect(button).not.toBeDisabled()
      })
    })

    describe('when an EAN search is performed succesfully', () => {
      beforeEach(() => {
        vi.spyOn(api, 'getProductByEan').mockResolvedValue({
          id: 0,
          name: 'Music has the right to children',
          description: 'An album by Boards of Canada',
          subcategoryId: 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE',
          gtlId: '08000000',
          author: 'Boards of Canada',
          performer: 'Boards of Canada',
          images: {},
        })

        renderDetailsEanSearch({ props: { isOfferProductBased: false } })
      })

      it('should display a success message', async () => {
        const button = screen.getByRole('button', { name: buttonLabel })
        const eanInput = screen.getByRole('textbox', { name: inputLabel })

        expect(screen.queryByText(successMessage)).not.toBeInTheDocument()

        await userEvent.type(eanInput, '9781234567897')
        await userEvent.click(button)

        expect(screen.queryByText(successMessage)).toBeInTheDocument()
      })

      it('should be disabled until the input is cleared', async () => {
        const button = screen.getByRole('button', { name: buttonLabel })
        const eanInput = screen.getByRole('textbox', { name: inputLabel })

        expect(eanInput).not.toBeDisabled()
        await userEvent.type(eanInput, '9781234567897')

        expect(button).not.toBeDisabled()
        await userEvent.click(button)

        expect(eanInput).toBeDisabled()
        expect(button).toBeDisabled()

        // A clear button appears, when clicked, it should empty
        // the input. The search button remains disabled, as
        // the input is empty.
        const clearButton = screen.getByRole('button', {
          name: clearButtonLabel,
        })
        expect(clearButton).toBeInTheDocument()
        await userEvent.click(clearButton)

        const newEanInput = screen.getByRole('textbox', { name: inputLabel })
        expect(newEanInput).not.toBeDisabled()
        expect(newEanInput).toHaveValue('')
        expect(button).toBeDisabled()
      })
    })

    describe('when an EAN search ends with an API error (only)', () => {
      beforeEach(() => {
        vi.spyOn(api, 'getProductByEan').mockRejectedValue(new Error('error'))
        renderDetailsEanSearch({ props: { isOfferProductBased: false } })
      })

      it('should display an error message', async () => {
        const button = screen.getByRole('button', { name: buttonLabel })
        const eanInput = screen.getByRole('textbox', { name: inputLabel })

        expect(screen.queryByText(errorMessage)).not.toBeInTheDocument()

        await userEvent.type(eanInput, '9781234567897')
        await userEvent.click(button)

        expect(screen.queryByText(errorMessage)).toBeInTheDocument()
      })

      it('should disable the submit button', async () => {
        const button = screen.getByRole('button', { name: buttonLabel })
        const eanInput = screen.getByRole('textbox', { name: inputLabel })

        await userEvent.type(eanInput, '9781234567897')

        expect(button).not.toBeDisabled()
        await userEvent.click(button)

        expect(button).toBeDisabled()
      })
    })
  })

  describe('after POST request (the form has been submitted)', () => {
    describe('when an EAS search was performed succesfully', () => {
      beforeEach(() => {
        renderDetailsEanSearch({ props: { isOfferProductBased: true } })
      })

      it('should not display the clear button anymore', () => {
        const clearButton = screen.queryByRole('button', {
          name: clearButtonLabel,
        })
        expect(clearButton).not.toBeInTheDocument()
      })

      it('should display an info message', () => {
        expect(screen.queryByText(infoMessage)).toBeInTheDocument()
      })
    })
  })
})
