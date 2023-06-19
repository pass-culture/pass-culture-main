import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
  setDefaultInitialFormValues,
} from 'components/OfferIndividualForm'
import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'

import { validationSchema, Venue, VENUE_DEFAULT_VALUES } from '..'
import { IVenueProps } from '../Venue'

const renderVenue = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: Partial<IOfferIndividualFormValues>
  onSubmit: () => void
  props: IVenueProps
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Venue {...props} />
    </Formik>
  )
}

describe('OfferIndividual section: venue', () => {
  let initialValues: Partial<IOfferIndividualFormValues>
  let props: IVenueProps
  const onSubmit = jest.fn()
  let venueList: TOfferIndividualVenue[]
  const firstOfferer = {
    id: 'AE',
    nonHumanizedId: 1,
    name: 'Offerer AE',
  }
  const secondOfferer = {
    id: 'A9',
    nonHumanizedId: 2,
    name: 'Offerer A9',
  }
  const thirdOfferer = {
    id: 'AM',
    nonHumanizedId: 3,
    name: 'Offerer AM',
  }

  beforeEach(() => {
    const offererNames: TOffererName[] = [
      firstOfferer,
      secondOfferer,
      thirdOfferer,
    ]

    venueList = [
      {
        nonHumanizedId: 1,
        name: 'Venue AAAA',
        managingOffererId: 'AE',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
        hasMissingReimbursementPoint: false,
        hasCreatedOffer: true,
      },
      {
        nonHumanizedId: 2,
        name: 'Venue BBAA',
        managingOffererId: 'A9',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
        hasMissingReimbursementPoint: false,
        hasCreatedOffer: true,
      },
      {
        nonHumanizedId: 3,
        name: 'Venue CCAA',
        managingOffererId: 'AM',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
        hasMissingReimbursementPoint: false,
        hasCreatedOffer: true,
      },
      {
        nonHumanizedId: 4,
        name: 'Venue CCBB',
        managingOffererId: 'AM',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
        hasMissingReimbursementPoint: false,
        hasCreatedOffer: true,
      },
    ]

    initialValues = setDefaultInitialFormValues(
      FORM_DEFAULT_VALUES,
      offererNames,
      null,
      null,
      venueList
    )
    props = {
      offererNames,
      venueList,
    }
  })

  it('should not automatically select a structure', async () => {
    renderVenue({
      initialValues,
      onSubmit,
      props,
    })

    const selectOfferer = screen.getByLabelText('Structure')

    expect(selectOfferer).toBeInTheDocument()
    expect(selectOfferer).toHaveValue(VENUE_DEFAULT_VALUES.offererId)
    expect(selectOfferer.childNodes.length).toBe(4)
  })

  it('should not automatically select an offerer when the structure is not defined', async () => {
    renderVenue({
      initialValues,
      onSubmit,
      props,
    })
    const selectVenue = screen.getByLabelText('Lieu')

    expect(selectVenue).toBeInTheDocument()
    expect(selectVenue).toHaveValue(VENUE_DEFAULT_VALUES.venueId)
    expect(selectVenue).toBeDisabled()
    expect(selectVenue.childNodes.length).toBe(1)
  })

  it('should automatically select the venue and offerer when there is only one in the list', async () => {
    props = {
      offererNames: [props.offererNames[0]],
      venueList: [props.venueList[0]],
    }
    initialValues = setDefaultInitialFormValues(
      FORM_DEFAULT_VALUES,
      props.offererNames,
      null,
      null,
      props.venueList
    )
    renderVenue({
      initialValues,
      onSubmit,
      props,
    })
    const selectVenue = screen.getByLabelText('Lieu')
    const selectOfferer = screen.getByLabelText('Structure')

    await waitFor(() => {
      expect(selectOfferer).toHaveValue(firstOfferer.nonHumanizedId.toString())
      expect(selectOfferer).toBeDisabled()
      expect(selectOfferer.childNodes.length).toBe(1)
      expect(selectVenue).toHaveValue(venueList[0].nonHumanizedId.toString())
      expect(selectVenue).toBeDisabled()
      expect(selectVenue.childNodes.length).toBe(1)
    })
  })

  it('should automaticaly select the venue when only one option is available', async () => {
    renderVenue({
      initialValues,
      onSubmit,
      props,
    })
    const selectVenue = screen.getByLabelText('Lieu')
    const selectOfferer = screen.getByLabelText('Structure')

    // select a offerer with 1 venue
    await userEvent.selectOptions(
      selectOfferer,
      firstOfferer.nonHumanizedId.toString()
    )
    expect(selectOfferer).toHaveValue(firstOfferer.nonHumanizedId.toString())

    expect(selectVenue).toBeDisabled()
    expect(selectVenue).toHaveValue(venueList[0].nonHumanizedId.toString())
    expect(selectVenue.childNodes.length).toBe(1)
  })

  it('should not automaticaly select the venue when multiple options are available', async () => {
    renderVenue({
      initialValues,
      onSubmit,
      props,
    })
    const selectVenue = screen.getByLabelText('Lieu')
    const selectOfferer = screen.getByLabelText('Structure')

    await userEvent.selectOptions(
      selectOfferer,
      thirdOfferer.nonHumanizedId.toString()
    )
    expect(selectOfferer).toHaveValue(thirdOfferer.nonHumanizedId.toString())

    await waitFor(() => {
      expect(selectVenue).not.toBeDisabled()
    })

    expect(selectVenue.childNodes.length).toBe(3)
    expect(selectVenue).toHaveValue(VENUE_DEFAULT_VALUES.venueId)
  })

  it('should automatically unselect the venue when the user unselects the offerer', async () => {
    renderVenue({
      initialValues,
      onSubmit,
      props,
    })
    const selectVenue = screen.getByLabelText('Lieu')
    const selectOfferer = screen.getByLabelText('Structure')

    // select a other offerer with 1 venue
    await userEvent.selectOptions(
      selectOfferer,
      secondOfferer.nonHumanizedId.toString()
    )

    // unselect offerer id
    await userEvent.selectOptions(selectOfferer, 'Selectionner une structure')

    expect(selectVenue).toHaveValue(VENUE_DEFAULT_VALUES.venueId)
    expect(selectVenue).toBeDisabled()
    expect(selectVenue.childNodes.length).toBe(1)
  })

  it('should display an error when the user has not filled all required fields', async () => {
    renderVenue({
      initialValues,
      onSubmit,
      props,
    })
    const selectVenue = screen.getByLabelText('Lieu')
    const selectOfferer = screen.getByLabelText('Structure')

    expect(
      screen.queryByText('Veuillez sélectionner une structure')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Veuillez sélectionner un lieu')
    ).not.toBeInTheDocument()

    await userEvent.selectOptions(
      selectOfferer,
      thirdOfferer.nonHumanizedId.toString()
    )
    await userEvent.selectOptions(selectVenue, 'Venue CCBB')

    await userEvent.selectOptions(selectVenue, 'Sélectionner un lieu')
    await userEvent.tab()
    await waitFor(() =>
      expect(
        screen.getByText('Veuillez sélectionner un lieu')
      ).toBeInTheDocument()
    )

    await userEvent.selectOptions(selectOfferer, 'Selectionner une structure')
    await userEvent.tab()

    await waitFor(() => {
      expect(
        screen.getByText('Veuillez sélectionner une structure')
      ).toBeInTheDocument()
      expect(
        screen.queryByText('Veuillez sélectionner un lieu')
      ).not.toBeInTheDocument()
    })
  })

  it('should disable read only fields', () => {
    props.readOnlyFields = ['venueId', 'offererId']

    renderVenue({
      initialValues,
      onSubmit,
      props,
    })

    expect(screen.getByLabelText('Structure')).toBeDisabled()
    expect(screen.getByLabelText('Lieu')).toBeDisabled()
  })
})
