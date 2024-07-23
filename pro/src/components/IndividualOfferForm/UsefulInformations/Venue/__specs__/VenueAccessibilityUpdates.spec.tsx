import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { Accessibility } from 'components/IndividualOfferForm/Accessibility/Accessibility'
import { AccessibilityFormValues, AccessibilityEnum } from 'core/shared/types'
import {
  getOffererNameFactory,
  venueListItemFactory,
} from 'utils/individualApiFactories'
import {
  renderWithProviders,
  RenderWithProvidersOptions,
} from 'utils/renderWithProviders'

import { Venue, VenueProps } from '../Venue'

interface InitialValues {
  offererId: string
  venueId: string
  accessibility: AccessibilityFormValues
}

const renderVenue = ({
  initialValues,
  onSubmit = vi.fn(),
  venueProps,
  options,
}: {
  initialValues: InitialValues
  onSubmit: () => void
  venueProps: VenueProps
  options?: RenderWithProvidersOptions
}) => {
  const rtlReturn = renderWithProviders(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object()}
    >
      <>
        <Venue {...venueProps} />
        <Accessibility />
      </>
    </Formik>,
    options
  )

  const selectVenue = screen.getByLabelText('Lieu *')
  const checkboxNone = screen.getByLabelText('Non accessible', {
    exact: false,
  })
  const checkboxVisuel = screen.getByLabelText('Visuel', { exact: false })
  const checkboxMental = screen.getByLabelText('Psychique ou cognitif', {
    exact: false,
  })
  const checkboxMoteur = screen.getByLabelText('Moteur', { exact: false })
  const checkboxAuditif = screen.getByLabelText('Auditif', { exact: false })

  return {
    ...rtlReturn,
    selectVenue,
    checkboxNone,
    checkboxVisuel,
    checkboxMental,
    checkboxMoteur,
    checkboxAuditif,
  }
}

describe('IndividualOffer section: venue', () => {
  let initialValues: InitialValues
  let venueProps: VenueProps
  let venueAccessible: VenueListItemResponseModel
  let venueNotAccessible: VenueListItemResponseModel
  const onSubmit = vi.fn()

  beforeEach(() => {
    const offererNames: GetOffererNameResponseModel[] = [
      getOffererNameFactory({
        id: 1,
        name: 'Offerer AE',
      }),
    ]

    venueAccessible = venueListItemFactory({
      visualDisabilityCompliant: false,
      mentalDisabilityCompliant: true,
      audioDisabilityCompliant: true,
      motorDisabilityCompliant: false,
    })
    venueNotAccessible = venueListItemFactory({
      visualDisabilityCompliant: false,
      mentalDisabilityCompliant: false,
      audioDisabilityCompliant: false,
      motorDisabilityCompliant: false,
    })
    const venueList: VenueListItemResponseModel[] = [
      venueAccessible,
      venueNotAccessible,
    ]

    initialValues = {
      offererId: '1',
      venueId: '',
      accessibility: {
        [AccessibilityEnum.VISUAL]: false,
        [AccessibilityEnum.MENTAL]: false,
        [AccessibilityEnum.AUDIO]: false,
        [AccessibilityEnum.MOTOR]: false,
        [AccessibilityEnum.NONE]: false,
      },
    }
    venueProps = {
      offererNames,
      venueList,
    }
  })

  it('should fill accessibilities when venue change', async () => {
    const {
      selectVenue,
      checkboxNone,
      checkboxVisuel,
      checkboxMental,
      checkboxMoteur,
      checkboxAuditif,
    } = renderVenue({ initialValues, onSubmit, venueProps })

    await screen.findByRole('heading', { name: 'Accessibilité' })

    await userEvent.selectOptions(selectVenue, venueAccessible.id.toString())
    expect(checkboxVisuel).not.toBeChecked()
    expect(checkboxMental).toBeChecked()
    expect(checkboxAuditif).toBeChecked()
    expect(checkboxMoteur).not.toBeChecked()
    expect(checkboxNone).not.toBeChecked()

    await userEvent.selectOptions(selectVenue, venueNotAccessible.id.toString())
    expect(checkboxVisuel).not.toBeChecked()
    expect(checkboxMental).not.toBeChecked()
    expect(checkboxAuditif).not.toBeChecked()
    expect(checkboxMoteur).not.toBeChecked()
    expect(checkboxNone).toBeChecked()

    await userEvent.click(checkboxVisuel)
    expect(checkboxNone).not.toBeChecked()
    expect(checkboxVisuel).toBeChecked()
  })
})
