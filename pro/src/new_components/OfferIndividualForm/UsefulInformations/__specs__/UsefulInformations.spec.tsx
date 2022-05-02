import '@testing-library/jest-dom'

import * as yup from 'yup'

import { UsefulInformations, validationSchema } from '..'
import { render, screen } from '@testing-library/react'

import { Formik } from 'formik'
import { IUsefulInformationsProps } from '../UsefulInformations'
import React from 'react'
import { TOfferIndividualVenue } from 'core/Venue/types'
import { TOffererName } from 'core/Offerers/types'

interface IInitialValues {
  offererId: string
  venueId: string
}

const renderUsefulInformations = ({
  initialValues,
  onSubmit = jest.fn(),
  props,
}: {
  initialValues: IInitialValues
  onSubmit: () => void
  props: IUsefulInformationsProps
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <UsefulInformations {...props} />
    </Formik>
  )
}

describe('OfferIndividual section: UsefulInformations', () => {
  let initialValues: IInitialValues
  let props: IUsefulInformationsProps
  const onSubmit = jest.fn()

  beforeEach(() => {
    const offererNames: TOffererName[] = [
      {
        id: 'AA',
        name: 'Offerer AA',
      },
    ]

    const venueList: TOfferIndividualVenue[] = [
      {
        id: 'AAAA',
        name: 'Venue AAAA',
        managingOffererId: 'AA',
        isVirtual: false,
      },
    ]

    initialValues = {
      offererId: '',
      venueId: '',
    }
    props = {
      offererNames,
      venueList,
      isUserAdmin: false,
    }
  })

  it('should render the component', async () => {
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })
    expect(
      await screen.findByRole('heading', { name: 'Informations pratiques' })
    ).toBeInTheDocument()
    expect(
      screen.queryByLabelText('Rayonnement national')
    ).not.toBeInTheDocument()
  })

  it('should contain isNational when user is admin', async () => {
    props.isUserAdmin = true
    renderUsefulInformations({
      initialValues,
      onSubmit,
      props,
    })
    await screen.findByRole('heading', { name: 'Informations pratiques' })
    expect(screen.getByLabelText('Rayonnement national')).toBeInTheDocument()
  })
})
