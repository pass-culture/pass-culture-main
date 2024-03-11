import { render, screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import {
  GetOffererNameResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import {
  IndividualOfferFormValues,
  setDefaultInitialFormValues,
} from 'components/IndividualOfferForm'
import { venueListItemFactory } from 'utils/individualApiFactories'

import { validationSchema, Venue, VENUE_DEFAULT_VALUES } from '..'
import { VenueProps } from '../Venue'

const renderVenue = ({
  initialValues,
  onSubmit = vi.fn(),
  props,
}: {
  initialValues: Partial<IndividualOfferFormValues>
  onSubmit: () => void
  props: VenueProps
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

describe('IndividualOffer section: venue', () => {
  let initialValues: Partial<IndividualOfferFormValues>
  let props: VenueProps
  const onSubmit = vi.fn()
  let venueList: VenueListItemResponseModel[]
  const firstOfferer = {
    id: 1,
    name: 'Offerer AE',
    allowedOnAdage: true,
  }
  const secondOfferer = {
    id: 2,
    name: 'Offerer A9',
    allowedOnAdage: true,
  }
  const thirdOfferer = {
    id: 3,
    name: 'Offerer AM',
    allowedOnAdage: true,
  }

  beforeEach(() => {
    const offererNames: GetOffererNameResponseModel[] = [
      firstOfferer,
      secondOfferer,
      thirdOfferer,
    ]

    venueList = [
      venueListItemFactory({
        managingOffererId: firstOfferer.id,
      }),
      venueListItemFactory({
        managingOffererId: secondOfferer.id,
      }),
      venueListItemFactory({
        managingOffererId: thirdOfferer.id,
      }),
      venueListItemFactory({
        name: 'Venue CCBB',
        managingOffererId: thirdOfferer.id,
      }),
    ]

    initialValues = setDefaultInitialFormValues(
      offererNames,
      null,
      null,
      venueList,
      true
    )
    props = {
      offererNames,
      venueList,
    }
  })

  it('should not automatically select a structure', () => {
    renderVenue({ initialValues, onSubmit, props })

    const selectOfferer = screen.getByLabelText('Structure *')

    expect(selectOfferer).toBeInTheDocument()
    expect(selectOfferer).toHaveValue(VENUE_DEFAULT_VALUES.offererId)
    expect(selectOfferer.childNodes.length).toBe(4)
  })

  it('should not automatically select an offerer when the structure is not defined', () => {
    renderVenue({ initialValues, onSubmit, props })

    const selectVenue = screen.getByLabelText('Lieu *')

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
      props.offererNames,
      null,
      null,
      props.venueList,
      true
    )
    renderVenue({
      initialValues,
      onSubmit,
      props,
    })
    const selectVenue = screen.getByLabelText('Lieu *')
    const selectOfferer = screen.getByLabelText('Structure *')

    await waitFor(() => {
      expect(selectOfferer).toHaveValue(firstOfferer.id.toString())
      expect(selectOfferer).toBeDisabled()
      expect(selectOfferer.childNodes.length).toBe(1)
      expect(selectVenue).toHaveValue(venueList[0].id.toString())
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
    const selectVenue = screen.getByLabelText('Lieu *')
    const selectOfferer = screen.getByLabelText('Structure *')

    // select a offerer with 1 venue
    await userEvent.selectOptions(selectOfferer, firstOfferer.id.toString())
    expect(selectOfferer).toHaveValue(firstOfferer.id.toString())

    expect(selectVenue).toBeDisabled()
    expect(selectVenue).toHaveValue(venueList[0].id.toString())
    expect(selectVenue.childNodes.length).toBe(1)
  })

  it('should not automaticaly select the venue when multiple options are available', async () => {
    renderVenue({
      initialValues,
      onSubmit,
      props,
    })
    const selectVenue = screen.getByLabelText('Lieu *')
    const selectOfferer = screen.getByLabelText('Structure *')

    await userEvent.selectOptions(selectOfferer, thirdOfferer.id.toString())
    expect(selectOfferer).toHaveValue(thirdOfferer.id.toString())

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
    const selectVenue = screen.getByLabelText('Lieu *')
    const selectOfferer = screen.getByLabelText('Structure *')

    // select a other offerer with 1 venue
    await userEvent.selectOptions(selectOfferer, secondOfferer.id.toString())

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
    const selectVenue = screen.getByLabelText('Lieu *')
    const selectOfferer = screen.getByLabelText('Structure *')

    expect(
      screen.queryByText('Veuillez sélectionner une structure')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Veuillez sélectionner un lieu')
    ).not.toBeInTheDocument()

    await userEvent.selectOptions(selectOfferer, thirdOfferer.id.toString())
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

    expect(screen.getByLabelText('Structure *')).toBeDisabled()
    expect(screen.getByLabelText('Lieu *')).toBeDisabled()
  })
})
