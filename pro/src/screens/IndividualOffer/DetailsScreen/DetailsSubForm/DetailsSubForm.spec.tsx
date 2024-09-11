import { screen } from '@testing-library/react'
import { FormikProvider, useFormik } from 'formik'

import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'context/IndividualOfferContext/IndividualOfferContext'
import { renderWithProviders } from 'utils/renderWithProviders'

import { DEFAULT_DETAILS_FORM_VALUES } from '../constants'

import {
  DetailsSubForm,
  DetailsSubFormProps,
  ARTISTIC_INFORMATION_FIELDS,
} from './DetailsSubForm'

const contextValue: IndividualOfferContextValues = {
  categories: [],
  subCategories: [],
  offer: null,
  isEvent: null,
  setIsEvent: vi.fn(),
}

type RequiredProps = 'isProductBased' | 'isOfferCDOrVinyl'
type DetailsSubFormTestProps = Partial<Pick<DetailsSubFormProps, RequiredProps>>

const DetailsSubFormWrappedWithFormik = ({
  isProductBased = false,
  isOfferCDOrVinyl = false,
}: DetailsSubFormTestProps) => {
  const formik = useFormik({
    initialValues: {
      ...DEFAULT_DETAILS_FORM_VALUES,
      subcategoryConditionalFields: ARTISTIC_INFORMATION_FIELDS,
    },
    onSubmit: vi.fn(),
  })

  return (
    <FormikProvider value={formik}>
      <DetailsSubForm
        isProductBased={isProductBased}
        isOfferCDOrVinyl={isOfferCDOrVinyl}
        readOnlyFields={[]}
        onImageUpload={vi.fn()}
        onImageDelete={vi.fn()}
      />
    </FormikProvider>
  )
}

const renderDetailsSubForm = (args?: DetailsSubFormTestProps) => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <DetailsSubFormWrappedWithFormik {...args} />
    </IndividualOfferContext.Provider>
  )
}

describe('DetailsSubForm', () => {
  it('should display conditional fields based on the selected category', () => {
    renderDetailsSubForm()

    const subFormTextInputs = {
      speaker: /Intervenant/,
      author: /Auteur/,
      visa: /Visa/,
      stageDirector: /Metteur en scène/,
      performer: /Interprète/,
      ean: /EAN/,
    }

    Object.values(subFormTextInputs).forEach((input) => {
      const inputElement = screen.getByRole('textbox', { name: input })
      expect(inputElement).toBeInTheDocument()
    })

    const subFormSelects = {
      gtl_id: /Genre musical/,
      showType: /Type de spectacle/,
    }

    Object.values(subFormSelects).forEach((select) => {
      const selectElement = screen.getByRole('combobox', { name: select })
      expect(selectElement).toBeInTheDocument()
    })

    const subFormDurationInput = screen.getByLabelText(/Durée/)
    expect(subFormDurationInput).toBeInTheDocument()
  })

  describe('when the offer is product-based', () => {
    it('should not display the EAN field since it would duplicate top EAN search/input field', () => {
      renderDetailsSubForm({ isProductBased: true })

      const eanInput = screen.queryByRole('textbox', { name: /EAN/ })
      expect(eanInput).not.toBeInTheDocument()
    })
  })

  describe('when the offer is non-product based', () => {
    it('should display a callout instead when the offer is a CD/vinyl', () => {
      renderDetailsSubForm({
        isProductBased: false,
        isOfferCDOrVinyl: true,
      })

      const calloutWrapper = screen.getByRole('alert')
      const calloutLabel = /Cette catégorie nécessite un EAN./
      expect(calloutWrapper).toBeInTheDocument()
      expect(calloutWrapper).toHaveTextContent(calloutLabel)
    })
  })
})
