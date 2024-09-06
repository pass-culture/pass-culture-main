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

const EanSearchWrappedWithFormik = ({
  isClearAvailable,
}: {
  isClearAvailable: boolean
}): JSX.Element => {
  const formik = useFormik({
    initialValues: DEFAULT_DETAILS_FORM_VALUES,
    onSubmit: vi.fn(),
  })

  const setImageOffer: DetailsEanSearchProps['setImageOffer'] = vi.fn()

  return (
    <FormikProvider value={formik}>
      <DetailsEanSearch
        setImageOffer={setImageOffer}
        isClearAvailable={isClearAvailable}
      />
    </FormikProvider>
  )
}

const renderDetailsEanSearch = ({
  isClearAvailable,
}: {
  isClearAvailable: boolean
}) => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <EanSearchWrappedWithFormik isClearAvailable={isClearAvailable} />
    </IndividualOfferContext.Provider>
  )
}

vi.mock('apiClient/api', () => ({
  api: { getProductByEan: vi.fn() },
}))

const buttonLabel = 'Rechercher'
const inputLabel = 'Nouveau Scanner ou rechercher un produit par EAN'
const successMessage =
  'Les informations suivantes ont été synchronisées' +
  ' à partir de l’EAN renseigné.'
const errorMessage = 'Une erreur est survenue lors de la recherche'
const clearButtonLabel = /Effacer/

describe('DetailsEanSearch', () => {
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
    })

    it('should display a success message', async () => {
      renderDetailsEanSearch({ isClearAvailable: true })

      const button = screen.getByRole('button', { name: buttonLabel })
      const eanInput = screen.getByRole('textbox', { name: inputLabel })

      expect(screen.queryByText(successMessage)).not.toBeInTheDocument()

      await userEvent.type(eanInput, '9781234567897')
      await userEvent.click(button)

      expect(screen.queryByText(successMessage)).toBeInTheDocument()
    })

    it('should be disabled until the input is cleared', async () => {
      renderDetailsEanSearch({ isClearAvailable: true })

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
      const clearButton = screen.getByRole('button', { name: clearButtonLabel })
      expect(clearButton).toBeInTheDocument()
      await userEvent.click(clearButton)

      const newEanInput = screen.getByRole('textbox', { name: inputLabel })
      expect(newEanInput).not.toBeDisabled()
      expect(newEanInput).toHaveValue('')
      expect(button).toBeDisabled()
    })

    it('should not display the clear button afterwards if unavailable (POST draft/edited offer contexts)', async () => {
      renderDetailsEanSearch({ isClearAvailable: false })

      const button = screen.getByRole('button', { name: buttonLabel })
      const eanInput = screen.getByRole('textbox', { name: inputLabel })

      await userEvent.type(eanInput, '9781234567897')
      await userEvent.click(button)

      const clearButton = screen.queryByRole('button', {
        name: clearButtonLabel,
      })
      expect(clearButton).not.toBeInTheDocument()
    })
  })

  describe('when an EAN search ends with an error', () => {
    beforeEach(() => {
      vi.spyOn(api, 'getProductByEan').mockRejectedValue(new Error('error'))
      renderDetailsEanSearch({ isClearAvailable: true })
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
