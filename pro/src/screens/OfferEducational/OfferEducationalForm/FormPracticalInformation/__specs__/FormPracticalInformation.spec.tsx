import { render, screen } from '@testing-library/react'
import { Formik } from 'formik'
import React from 'react'

import { OfferAddressType } from 'apiClient/v1'
import { IOfferEducationalFormValues } from 'core/OfferEducational'
import {
  EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
  INTERVENTION_AREA_LABEL,
  PRICE_INFORMATION,
} from 'screens/OfferEducational/constants/labels'
import { offererFactory, venueFactory } from 'utils/apiFactories'

import FormPracticalInformation, {
  IFormPracticalInformationProps,
} from '../FormPracticalInformation'

const renderFormPracticalInformation = (
  props: IFormPracticalInformationProps,
  initialValues: Pick<
    IOfferEducationalFormValues,
    'eventAddress' | 'priceDetail' | 'interventionArea'
  >
) => {
  render(
    <Formik initialValues={initialValues} onSubmit={() => {}}>
      <FormPracticalInformation {...props} />
    </Formik>
  )
}

describe('FormPracticalInformation', () => {
  let props: IFormPracticalInformationProps
  let initialValues: Pick<
    IOfferEducationalFormValues,
    'eventAddress' | 'priceDetail' | 'interventionArea'
  >

  beforeAll(() => {
    props = {
      isTemplate: false,
      venuesOptions: [
        { label: 'VENUE_1', value: 'V1' },
        { label: 'VENUE_2', value: 'V2' },
      ],
      currentOfferer: {
        ...offererFactory({}),
        managedVenues: [
          venueFactory({ id: 'V1', publicName: 'Venue1', name: 'Venue1' }),
          venueFactory({ id: 'V2', publicName: 'Venue2', name: 'Venue2' }),
        ],
      },
      disableForm: false,
    }

    initialValues = {
      eventAddress: {
        venueId: 'V1',
        addressType: OfferAddressType.OFFERER_VENUE,
        otherAddress: '',
      },
      interventionArea: [],
    }
  })

  describe('price detail', () => {
    it('should render price detail when offer is template', () => {
      renderFormPracticalInformation(
        { ...props, isTemplate: true },
        initialValues
      )

      expect(
        screen.getByLabelText(PRICE_INFORMATION, { exact: false })
      ).toBeInTheDocument()
    })

    it('should not render price detail when offer is not template', () => {
      renderFormPracticalInformation(props, initialValues)

      expect(
        screen.queryByLabelText(PRICE_INFORMATION, { exact: false })
      ).not.toBeInTheDocument()
    })
  })

  describe('eventAddress conditionnal render', () => {
    it('should render banner with venue information when offerer venue is selected', () => {
      renderFormPracticalInformation(props, initialValues)

      expect(screen.getByText(/Venue1/)).toBeInTheDocument()
      const textarea = screen.queryByRole('textbox', {
        name: EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
      })
      expect(textarea).not.toBeInTheDocument()
      expect(
        screen.queryByLabelText(INTERVENTION_AREA_LABEL)
      ).not.toBeInTheDocument()
    })

    it('should render textarea and mobility zone when other venue is selected', () => {
      renderFormPracticalInformation(props, {
        ...initialValues,
        eventAddress: {
          addressType: OfferAddressType.OTHER,
          otherAddress: 'A la mairie',
          venueId: '',
        },
      })

      const textarea = screen.getByRole('textbox', {
        name: EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
      })
      expect(textarea).toBeInTheDocument()
      expect(textarea).toHaveValue('A la mairie')
      expect(
        screen.queryByLabelText(INTERVENTION_AREA_LABEL)
      ).toBeInTheDocument()
    })

    it('should render only mobility zone when school is selected', () => {
      renderFormPracticalInformation(props, {
        ...initialValues,
        eventAddress: {
          addressType: OfferAddressType.SCHOOL,
          otherAddress: '',
          venueId: '',
        },
      })

      const textarea = screen.queryByRole('textbox', {
        name: EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
      })
      expect(textarea).not.toBeInTheDocument()
      expect(
        screen.queryByLabelText(INTERVENTION_AREA_LABEL)
      ).toBeInTheDocument()
    })
  })
})
