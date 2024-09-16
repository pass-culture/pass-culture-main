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

type RequiredProps =
  | 'isEanSearchDisplayed'
  | 'isProductBased'
  | 'isOfferCDOrVinyl'
type DetailsSubFormTestProps = Partial<Pick<DetailsSubFormProps, RequiredProps>>

const DetailsSubFormWrappedWithFormik = ({
  isEanSearchDisplayed = false,
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
        isEanSearchDisplayed={isEanSearchDisplayed}
        isProductBased={isProductBased}
        isOfferCDOrVinyl={isOfferCDOrVinyl}
        readOnlyFields={[]}
        onImageUpload={vi.fn()}
        onImageDelete={vi.fn()}
      />
    </FormikProvider>
  )
}

const renderDetailsSubForm = ({
  props,
  enableEANSearch = false,
}: {
  props?: DetailsSubFormTestProps
  enableEANSearch?: boolean
} = {}) => {
  return renderWithProviders(
    <IndividualOfferContext.Provider value={contextValue}>
      <DetailsSubFormWrappedWithFormik {...props} />
    </IndividualOfferContext.Provider>,
    enableEANSearch ? { features: ['WIP_EAN_CREATION'] } : {}
  )
}

const calloutLabel = /Cette catégorie nécessite un EAN./

describe('DetailsSubForm', () => {
  it('should always display conditional fields based on the selected category / subcategory', () => {
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

  describe('when EAN search is displayed', () => {
    describe('when the offer is product based', () => {
      it('should not display the EAN field since it would duplicate top EAN search/input field', () => {
        renderDetailsSubForm({
          props: {
            isEanSearchDisplayed: true,
            isProductBased: true,
          },
          enableEANSearch: true,
        })

        const eanInput = screen.queryByRole('textbox', { name: /EAN/ })
        expect(eanInput).not.toBeInTheDocument()
      })
    })

    describe('when the offer is non-product based', () => {
      describe('when the offer is a CD/vinyl', () => {
        it('should replace conditional fields with a subcategory related error callout', () => {
          renderDetailsSubForm({
            props: {
              isEanSearchDisplayed: true,
              isProductBased: false,
              isOfferCDOrVinyl: true,
            },
            enableEANSearch: true,
          })

          const calloutWrapper = screen.getByRole('alert')
          expect(calloutWrapper).toBeInTheDocument()
          expect(calloutWrapper).toHaveTextContent(calloutLabel)

          const anchorLink = screen.getByRole('link', { name: /EAN/ })
          expect(anchorLink).toBeInTheDocument()
          expect(anchorLink).toHaveAttribute('href', '#eanSearch')
        })
      })
    })
  })
})
