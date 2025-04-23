import { screen } from '@testing-library/react'
import { FormikProvider, useFormik } from 'formik'
import { Route, Routes } from 'react-router-dom'

import {
  IndividualOfferContext,
  IndividualOfferContextValues,
} from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { OFFER_WIZARD_MODE } from 'commons/core/Offers/constants'
import { getIndividualOfferPath } from 'commons/core/Offers/utils/getIndividualOfferUrl'
import { renderWithProviders } from 'commons/utils/renderWithProviders'
import { OFFER_WIZARD_STEP_IDS } from 'components/IndividualOfferNavigation/constants'
import { DEFAULT_DETAILS_FORM_VALUES } from 'pages/IndividualOffer/IndividualOfferDetails/commons/constants'

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

type RequiredProps = 'isEanSearchDisplayed' | 'isProductBased' | 'isOfferCD'
type DetailsSubFormTestProps = Partial<Pick<DetailsSubFormProps, RequiredProps>>

const DetailsSubFormWrappedWithFormik = ({
  isEanSearchDisplayed = false,
  isProductBased = false,
  isOfferCD = false,
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
        isOfferCD={isOfferCD}
        readOnlyFields={[]}
      />
    </FormikProvider>
  )
}

const renderDetailsSubForm = ({
  props,
  mode = OFFER_WIZARD_MODE.CREATION,
}: {
  props?: DetailsSubFormTestProps
  mode?: OFFER_WIZARD_MODE
} = {}) => {
  const path = getIndividualOfferPath({
    step: OFFER_WIZARD_STEP_IDS.DETAILS,
    mode,
  })
  const options = {
    initialRouterEntries: [path],
  }

  return renderWithProviders(
    <>
      <Routes>
        <Route
          path={path}
          element={
            <IndividualOfferContext.Provider value={contextValue}>
              <DetailsSubFormWrappedWithFormik {...props} />
            </IndividualOfferContext.Provider>
          }
        />
      </Routes>
    </>,
    options
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
      it('on creation, should not display the EAN field since it would duplicate top EAN search/input field', () => {
        renderDetailsSubForm({
          props: {
            isEanSearchDisplayed: true,
            isProductBased: true,
          },
          mode: OFFER_WIZARD_MODE.CREATION,
        })

        const eanInput = screen.queryByRole('textbox', { name: /EAN/ })
        expect(eanInput).not.toBeInTheDocument()
      })

      it('on edition, should display the EAN field', () => {
        renderDetailsSubForm({
          props: {
            isEanSearchDisplayed: true,
            isProductBased: true,
          },
          mode: OFFER_WIZARD_MODE.EDITION,
        })

        const eanInput = screen.getByRole('textbox', { name: /EAN/ })
        expect(eanInput).toBeInTheDocument()
      })
    })

    describe('when the offer is non-product based', () => {
      describe('when the offer is a CD', () => {
        it('should replace conditional fields with a subcategory related error callout', () => {
          renderDetailsSubForm({
            props: {
              isEanSearchDisplayed: true,
              isProductBased: false,
              isOfferCD: true,
            },
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
