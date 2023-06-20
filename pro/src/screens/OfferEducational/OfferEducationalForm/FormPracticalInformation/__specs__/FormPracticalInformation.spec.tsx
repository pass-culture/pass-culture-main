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
import { offererFactory, getOfferVenueFactory } from 'utils/apiFactories'

import FormPracticalInformation, {
  FormPracticalInformationProps,
} from '../FormPracticalInformation'

const renderFormPracticalInformation = (
  props: FormPracticalInformationProps,
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
  let props: FormPracticalInformationProps
  let initialValues: Pick<
    IOfferEducationalFormValues,
    | 'eventAddress'
    | 'priceDetail'
    | 'interventionArea'
    | 'search-domains'
    | 'search-interventionArea'
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
          {
            ...getOfferVenueFactory({
              id: 'V1',
              publicName: 'Venue1',
              name: 'Venue1',
            }),
            nonHumanizedId: 1,
          },
          {
            ...getOfferVenueFactory({
              id: 'V2',
              publicName: 'Venue2',
              name: 'Venue2',
            }),
            nonHumanizedId: 1,
          },
        ],
      },
      disableForm: false,
    }

    initialValues = {
      eventAddress: {
        venueId: 1,
        addressType: OfferAddressType.OFFERER_VENUE,
        otherAddress: '',
      },
      interventionArea: [],
      'search-domains': '',
      'search-interventionArea': '',
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
          venueId: null,
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
          venueId: null,
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
