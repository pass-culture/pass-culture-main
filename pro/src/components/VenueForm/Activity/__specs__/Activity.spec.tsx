import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { VenueFormValues } from 'components/VenueForm'
import { SubmitButton } from 'ui-kit'

import Activity, { ActivityProps } from '../Activity'
import { DEFAULT_ACTIVITY_FORM_VALUES } from '../constants'
import informationsValidationSchema from '../validationSchema'

const renderInformations = ({
  initialValues,
  onSubmit = vi.fn(),
  props,
}: {
  initialValues: Partial<VenueFormValues>
  onSubmit: () => void
  props: ActivityProps
}) => {
  const validationSchema = yup.object().shape(informationsValidationSchema)

  render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={validationSchema}
    >
      <Form>
        <Activity {...props} />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )
}

describe('Activity', () => {
  let props: ActivityProps
  let initialValues: Partial<VenueFormValues>
  const onSubmit = vi.fn()

  beforeEach(() => {
    initialValues = { ...DEFAULT_ACTIVITY_FORM_VALUES }
    props = {
      venueLabels: [],
      venueTypes: [{ value: 'CINEMA', label: 'Cinéma, salle de projection' }],
      isCreatingVenue: true,
    }
  })

  it('should submit form without errors', async () => {
    renderInformations({
      initialValues,
      onSubmit,
      props,
    })
    const buttonSubmit = screen.getByRole('button', {
      name: 'Submit',
    })
    const venueTypeSelect = screen.getByLabelText('Activité principale')
    await userEvent.selectOptions(venueTypeSelect, 'CINEMA')
    await userEvent.click(buttonSubmit)
    expect(onSubmit).toHaveBeenCalledTimes(1)
  })

  it('should validate required fields on submit', async () => {
    renderInformations({
      initialValues,
      onSubmit,
      props,
    })
    const venueTypeSelect = screen.getByLabelText('Activité principale')
    await userEvent.selectOptions(
      venueTypeSelect,
      'Sélectionnez celui qui correspond à votre lieu'
    )
    await userEvent.tab()
    expect(
      screen.getByText('Veuillez sélectionner une activité principale')
    ).toBeInTheDocument()
  })

  it('Should display less fields and infos when venue is virtual', () => {
    props.isVenueVirtual = true
    renderInformations({
      initialValues,
      onSubmit,
      props,
    })

    expect(screen.queryByTestId('wrapper-description')).not.toBeInTheDocument()
    expect(
      screen.queryByText(
        'Ces informations seront affichées dans votre page lieu sur l’application pass Culture (sauf pour les lieux administratifs). Elles permettront aux jeunes d’en savoir plus sur votre lieu.'
      )
    ).not.toBeInTheDocument()
    expect(screen.getByLabelText('Activité principale')).toBeDisabled()
  })
})
