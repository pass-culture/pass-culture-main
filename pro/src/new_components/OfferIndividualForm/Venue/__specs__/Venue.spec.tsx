import '@testing-library/jest-dom'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Formik } from 'formik'
import fetch from 'jest-fetch-mock'
import React from 'react'
import * as yup from 'yup'

import { TOffererName } from 'core/Offerers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { Venue, IVenueProps, validationSchema } from '..'

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

  it('test initial render', () => {
    const { selectVenue, selectOfferer } = renderVenue({
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

    expect(selectVenue).toBeInTheDocument()
    const venueDefaultOption = screen.getByRole('option', {
      name: 'Selectionner un lieu',
    }) as HTMLOptionElement
    expect(venueDefaultOption.selected).toBeTruthy()

    // Select venue disabled when offererId is not defined
    expect(selectVenue).toBeDisabled()
    expect(selectVenue.options.length).toBe(1)
  })

  it('test initial render with a single value for offerer and venue', async () => {
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

  it('test select a offerer id', async () => {
    const { selectVenue, selectOfferer } = renderVenue({
      initialValues,
      onSubmit,
      props,
    })

    let selectedOffererOption
    let selectedVenueOption

    // select a offerer with 1 venue
    await userEvent.selectOptions(selectOfferer, 'AA')
    selectedOffererOption = screen.getByRole('option', {
      name: 'Offerer AA',
    }) as HTMLOptionElement
    expect(selectedOffererOption.selected).toBeTruthy()

    expect(selectVenue).toBeDisabled()
    expect(selectVenue.options.length).toBe(1)
    selectedVenueOption = screen.getByRole('option', {
      name: 'Venue AAAA',
    }) as HTMLOptionElement
    expect(selectedVenueOption.selected).toBeTruthy()

    // select a other offerer with 1 venue
    await userEvent.selectOptions(selectOfferer, 'BB')
    selectedOffererOption = screen.getByRole('option', {
      name: 'Offerer BB',
    }) as HTMLOptionElement
    expect(selectedOffererOption.selected).toBeTruthy()

    expect(selectVenue).toBeDisabled()
    expect(selectVenue.options.length).toBe(1)
    selectedVenueOption = screen.getByRole('option', {
      name: 'Venue BBAA',
    }) as HTMLOptionElement
    expect(selectedVenueOption.selected).toBeTruthy()

    // select a other offerer with 2 venue
    await userEvent.selectOptions(selectOfferer, 'CC')
    selectedOffererOption = screen.getByRole('option', {
      name: 'Offerer CC',
    }) as HTMLOptionElement
    expect(selectedOffererOption.selected).toBeTruthy()

    expect(selectVenue).not.toBeDisabled()
    expect(selectVenue.options.length).toBe(3)
    selectedVenueOption = screen.getByRole('option', {
      name: 'Selectionner un lieu',
    }) as HTMLOptionElement
    expect(selectedVenueOption.selected).toBeTruthy()

    // unselect offerer id
    await userEvent.selectOptions(selectOfferer, 'Selectionner une structure')
    selectedOffererOption = screen.getByRole('option', {
      name: 'Selectionner une structure',
    }) as HTMLOptionElement
    expect(selectedOffererOption.selected).toBeTruthy()

    expect(selectVenue).toBeInTheDocument()
    const venueDefaultOption = screen.getByRole('option', {
      name: 'Selectionner un lieu',
    }) as HTMLOptionElement
    expect(venueDefaultOption.selected).toBeTruthy()
    expect(selectVenue).toBeDisabled()
    expect(selectVenue.options.length).toBe(1)
  })

  it.only('test required fields errors', async () => {
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
    await userEvent.click(document.body)
    expect(screen.getByText('Veuillez séléctioner un lieu')).toBeInTheDocument()

    await userEvent.selectOptions(selectOfferer, 'Selectionner une structure')
    await userEvent.click(document.body)
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
