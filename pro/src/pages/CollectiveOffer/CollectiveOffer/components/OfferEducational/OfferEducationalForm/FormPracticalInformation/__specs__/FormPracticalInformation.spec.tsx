import { screen } from '@testing-library/react'
import { FormProvider, useForm } from 'react-hook-form'

import { OfferAddressType } from '@/apiClient/v1'
import { getDefaultEducationalValues } from '@/commons/core/OfferEducational/constants'
import { OfferEducationalFormValues } from '@/commons/core/OfferEducational/types'
import {
  getOfferManagingOffererFactory,
  getOfferVenueFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import {
  EVENT_ADDRESS_OTHER_ADDRESS_LABEL,
  INTERVENTION_AREA_LABEL,
} from '../../../constants/labels'
import {
  FormPracticalInformation,
  FormPracticalInformationProps,
} from '../FormPracticalInformation'

function renderFormPracticalInformation(
  props: FormPracticalInformationProps,
  initialValues: Pick<
    OfferEducationalFormValues,
    'eventAddress' | 'priceDetail' | 'interventionArea'
  >
) {
  function FormPracticalInformationWrapper() {
    const form = useForm({
      defaultValues: { ...getDefaultEducationalValues(), ...initialValues },
    })

    return (
      <FormProvider {...form}>
        <FormPracticalInformation {...props} />
      </FormProvider>
    )
  }

  return renderWithProviders(<FormPracticalInformationWrapper />)
}

describe('FormPracticalInformation', () => {
  let props: FormPracticalInformationProps
  let initialValues: Pick<
    OfferEducationalFormValues,
    | 'eventAddress'
    | 'priceDetail'
    | 'interventionArea'
    | 'search-domains'
    | 'search-interventionArea'
  >

  beforeAll(() => {
    props = {
      venuesOptions: [
        { label: 'VENUE_1', value: 'V1' },
        { label: 'VENUE_2', value: 'V2' },
      ],
      currentOfferer: {
        ...getOfferManagingOffererFactory({}),
        managedVenues: [
          {
            ...getOfferVenueFactory({
              publicName: 'Venue1',
              name: 'Venue1',
            }),
            id: 1,
          },
          {
            ...getOfferVenueFactory({
              publicName: 'Venue2',
              name: 'Venue2',
            }),
            id: 1,
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
        name: 'Adresse de l’évènement *',
      })
      expect(textarea).toBeInTheDocument()
      expect(textarea).toHaveValue('A la mairie')
      expect(screen.queryByLabelText('Département(s)')).toBeInTheDocument()
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
        name: 'Adresse de l’évènement *',
      })
      expect(textarea).not.toBeInTheDocument()
      expect(screen.queryByLabelText('Département(s)')).toBeInTheDocument()
    })
  })
})
