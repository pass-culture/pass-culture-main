import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'

import { Venue, validationSchema } from '..'
import { IVenueProps } from '../Venue'

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
  const rtlReturns = render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Venue {...props} />
    </Formik>
  )

  const selectVenue = screen.getByLabelText('Lieu') as HTMLSelectElement
  const selectOfferer = screen.getByLabelText('Structure') as HTMLSelectElement

  return {
    ...rtlReturns,
    selectVenue,
    selectOfferer,
  }
}

describe('OfferIndividual section: venue', () => {
  let initialValues: IInitialValues
  let props: IVenueProps
  let onSubmit = jest.fn()

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
      },
      {
        id: 'BBAA',
        name: 'Venue BBAA',
        managingOffererId: 'BB',
      },
      {
        id: 'CCAA',
        name: 'Venue CCAA',
        managingOffererId: 'CC',
      },
      {
        id: 'CCBB',
        name: 'Venue CCBB',
        managingOffererId: 'CC',
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
    const { selectOfferer } = renderVenue({
      initialValues,
      onSubmit,
      props,
    })

    expect(selectOfferer).toBeInTheDocument()
    const offererDefaultOption = screen.getByRole('option', {
      name: 'Selectionner une structure',
    }) as HTMLOptionElement
    expect(offererDefaultOption.selected).toBeTruthy()
    expect(selectOfferer.options.length).toBe(4)
  })

  it('should not automatically select an offerer when the structure is not defined', () => {
    const { selectVenue } = renderVenue({
      initialValues,
      onSubmit,
      props,
    })

    expect(selectVenue).toBeInTheDocument()
    const venueDefaultOption = screen.getByRole('option', {
      name: 'Selectionner un lieu',
    }) as HTMLOptionElement
    expect(venueDefaultOption.selected).toBeTruthy()
    expect(selectVenue).toBeDisabled()
    expect(selectVenue.options.length).toBe(1)
  })

  it('should automatically select the venue and offerer when there is only one in the list', async () => {
    props = {
      offererNames: [props.offererNames[0]],
      venueList: [props.venueList[0]],
    }
    const { selectVenue, selectOfferer } = renderVenue({
      initialValues,
      onSubmit,
      props,
    })

    await waitFor(() => {
      const offererDefaultOption = screen.getByRole('option', {
        name: 'Offerer AA',
      }) as HTMLOptionElement
      expect(offererDefaultOption.selected).toBeTruthy()
      expect(selectVenue).toBeDisabled()
      expect(selectOfferer.options.length).toBe(1)

      const venueDefaultOption = screen.getByRole('option', {
        name: 'Venue AAAA',
      }) as HTMLOptionElement
      expect(venueDefaultOption.selected).toBeTruthy()
      expect(selectVenue).toBeDisabled()
      expect(selectVenue.options.length).toBe(1)
    })
  })

  it('should automaticaly select the venue when only one option is available', async () => {
    const { selectVenue, selectOfferer } = renderVenue({
      initialValues,
      onSubmit,
      props,
    })

    // select a offerer with 1 venue
    await userEvent.selectOptions(selectOfferer, 'AA')
    const selectedOffererOption = screen.getByRole('option', {
      name: 'Offerer AA',
    }) as HTMLOptionElement
    expect(selectedOffererOption.selected).toBeTruthy()

    expect(selectVenue).toBeDisabled()
    expect(selectVenue.options.length).toBe(1)
    const selectedVenueOption = screen.getByRole('option', {
      name: 'Venue AAAA',
    }) as HTMLOptionElement
    expect(selectedVenueOption.selected).toBeTruthy()
  })

  it('should not automaticaly select the venue when multiple options are available', async () => {
    const { selectVenue, selectOfferer } = renderVenue({
      initialValues,
      onSubmit,
      props,
    })

    await userEvent.selectOptions(selectOfferer, 'CC')
    const selectedOffererOption = screen.getByRole('option', {
      name: 'Offerer CC',
    }) as HTMLOptionElement
    expect(selectedOffererOption.selected).toBeTruthy()

    waitFor(() => {
      expect(selectVenue).not.toBeDisabled()
    })

    expect(selectVenue.options.length).toBe(3)
    const selectedVenueOption = screen.getByRole('option', {
      name: 'Selectionner un lieu',
    }) as HTMLOptionElement
    expect(selectedVenueOption.selected).toBeTruthy()
  })

  it('should automatically unselect the venue when the user unselects the offerer', async () => {
    const { selectVenue, selectOfferer } = renderVenue({
      initialValues,
      onSubmit,
      props,
    })

    // select a other offerer with 1 venue
    await userEvent.selectOptions(selectOfferer, 'BB')

    // unselect offerer id
    await userEvent.selectOptions(selectOfferer, 'Selectionner une structure')

    const venueDefaultOption = screen.getByRole('option', {
      name: 'Selectionner un lieu',
    }) as HTMLOptionElement
    expect(venueDefaultOption.selected).toBeTruthy()
    expect(selectVenue).toBeDisabled()
    expect(selectVenue.options.length).toBe(1)
  })

  it('should display an error when the user has not filled all required fields', async () => {
    const { selectVenue, selectOfferer } = renderVenue({
      initialValues,
      onSubmit,
      props,
    })
    expect(
      screen.queryByText('Veuillez séléctioner une structure')
    ).not.toBeInTheDocument()
    expect(
      screen.queryByText('Veuillez séléctioner un lieu')
    ).not.toBeInTheDocument()

    await userEvent.selectOptions(selectOfferer, 'Offerer CC')
    await userEvent.selectOptions(selectVenue, 'Venue CCBB')

    await userEvent.selectOptions(selectVenue, 'Selectionner un lieu')
    await userEvent.tab()
    waitFor(() =>
      expect(
        screen.getByText('Veuillez séléctioner un lieu')
      ).toBeInTheDocument()
    )

    await userEvent.selectOptions(selectOfferer, 'Selectionner une structure')
    await userEvent.tab()

    waitFor(() => {
      expect(
        screen.getByText('Veuillez séléctioner une structure')
      ).toBeInTheDocument()
      expect(
        screen.getByText('Veuillez séléctioner un lieu')
      ).not.toBeInTheDocument()
    })
  })
})
