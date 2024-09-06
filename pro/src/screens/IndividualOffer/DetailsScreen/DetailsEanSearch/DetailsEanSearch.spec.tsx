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

const EanSearchWrappedWithFormik = (): JSX.Element => {
  const formik = useFormik({
    initialValues: DEFAULT_DETAILS_FORM_VALUES,
    onSubmit: vi.fn(),
  })

  const setImageOffer: DetailsEanSearchProps['setImageOffer'] = vi.fn()

  return (
    <FormikProvider value={formik}>
      <DetailsEanSearch setImageOffer={setImageOffer} />
    </FormikProvider>
  )
}

const renderDetailsEanSearch = () => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <EanSearchWrappedWithFormik />
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
      renderDetailsEanSearch()
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

      // TODO: clear the input and test eanInput/button again.
    })
  })

  describe('when an EAN search ends with an error', () => {
    beforeEach(() => {
      vi.spyOn(api, 'getProductByEan').mockRejectedValue(new Error('error'))
      renderDetailsEanSearch()
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
