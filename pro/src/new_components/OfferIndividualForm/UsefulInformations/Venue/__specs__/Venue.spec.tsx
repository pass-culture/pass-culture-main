import '@testing-library/jest-dom'

import * as yup from 'yup'

import { VENUE_DEFAULT_VALUES, Venue, validationSchema } from '..'
import { render, screen, waitFor } from '@testing-library/react'

import { Formik } from 'formik'
import { IVenueProps } from '../Venue'
import React from 'react'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { TOffererName } from 'core/Offerers/types'
import userEvent from '@testing-library/user-event'

interface IInitialValues {
  offererId: string
  venueId: string
}

const renderVenue = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: IInitialValues
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
  let initialValues: IInitialValues
  let props: IVenueProps
  const onSubmit = jest.fn()

  beforeEach(() => {
    const offererNames: TOffererName[] = [
      {
        id: 'AA',
        name: 'Offerer AA',
      },
      {
        id: 'BB',
        name: 'Offerer BB',
      },
      {
        id: 'CC',
        name: 'Offerer CC',
      },
    ]

    const venueList: TOfferIndividualVenue[] = [
      {
        id: 'AAAA',
        name: 'Venue AAAA',
        managingOffererId: 'AA',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
      },
      {
        id: 'BBAA',
        name: 'Venue BBAA',
        managingOffererId: 'BB',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
      },
      {
        id: 'CCAA',
        name: 'Venue CCAA',
        managingOffererId: 'CC',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
      },
      {
        id: 'CCBB',
        name: 'Venue CCBB',
        managingOffererId: 'CC',
        isVirtual: false,
        withdrawalDetails: '',
        accessibility: {
          visual: false,
          mental: false,
          audio: false,
          motor: false,
          none: true,
        },
      },
    ]

    initialValues = {
      offererId: '',
      venueId: '',
    }
    props = {
      offererNames,
      venueList,
    }
  })

  it('should not automatically select a structure', () => {
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

  it('should not automatically select an offerer when the structure is not defined', () => {
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
    renderVenue({
      initialValues,
      onSubmit,
      props,
    })
    const selectVenue = screen.getByLabelText('Lieu')
    const selectOfferer = screen.getByLabelText('Structure')

    await waitFor(() => {
      expect(selectOfferer).toHaveValue('AA')
      expect(selectOfferer).toBeDisabled()
      expect(selectOfferer.childNodes.length).toBe(1)
      expect(selectVenue).toHaveValue('AAAA')
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
    await userEvent.selectOptions(selectOfferer, 'AA')
    expect(selectOfferer).toHaveValue('AA')

    expect(selectVenue).toBeDisabled()
    expect(selectVenue).toHaveValue('AAAA')
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

    await userEvent.selectOptions(selectOfferer, 'CC')
    expect(selectOfferer).toHaveValue('CC')

    waitFor(() => {
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
    await userEvent.selectOptions(selectOfferer, 'BB')

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

    await userEvent.selectOptions(selectOfferer, 'Offerer CC')
    await userEvent.selectOptions(selectVenue, 'Venue CCBB')

    await userEvent.selectOptions(selectVenue, 'Selectionner un lieu')
    await userEvent.tab()
    waitFor(() =>
      expect(
        screen.getByText('Veuillez sélectionner un lieu')
      ).toBeInTheDocument()
    )

    await userEvent.selectOptions(selectOfferer, 'Selectionner une structure')
    await userEvent.tab()

    waitFor(() => {
      expect(
        screen.getByText('Veuillez sélectionner une structure')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Veuillez sélectionner un lieu')
      ).not.toBeInTheDocument()
    })
  })
})
