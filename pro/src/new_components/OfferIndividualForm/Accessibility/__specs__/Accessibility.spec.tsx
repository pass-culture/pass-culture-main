import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { AccessiblityEnum, IAccessibiltyFormValues } from 'core/shared'
import { SubmitButton } from 'ui-kit'

import { Accessibility, validationSchema } from '..'

interface IInitialValues {
  offererId: string
  venueId: string
  subcategoryId: string
  withdrawalDetails: string
  withdrawalType: string
  withdrawalDelay: string
  accessibility: IAccessibiltyFormValues
}

const renderAccessibility = ({
  initialValues,
  onSubmit = jest.fn(),
}: {
  initialValues: IInitialValues
  onSubmit: () => void
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Form>
        <Accessibility />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )
}

describe('Accessibility', () => {
  let initialValues: IInitialValues
  const onSubmit = jest.fn()

  beforeEach(() => {
    initialValues = {
      offererId: '',
      venueId: '',
      subcategoryId: '',
      withdrawalDetails: '',
      withdrawalType: '',
      withdrawalDelay: '',
      accessibility: {
        [AccessiblityEnum.VISUAL]: false,
        [AccessiblityEnum.MENTAL]: false,
        [AccessiblityEnum.AUDIO]: false,
        [AccessiblityEnum.MOTOR]: false,
        [AccessiblityEnum.NONE]: false,
      },
    }
  })

  it('should display initial component', async () => {
    initialValues = {
      ...initialValues,
      accessibility: {
        [AccessiblityEnum.VISUAL]: false,
        [AccessiblityEnum.MENTAL]: false,
        [AccessiblityEnum.AUDIO]: false,
        [AccessiblityEnum.MOTOR]: false,
        [AccessiblityEnum.NONE]: false,
      },
    }
    await renderAccessibility({ initialValues, onSubmit })

    expect(
      await screen.findByRole('heading', { name: 'Accessibilité' })
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Cette offre est accessible au public en situation de handicap :'
      )
    ).toBeInTheDocument()

    expect(screen.getByLabelText('Visuel', { exact: false })).not.toBeChecked()
    expect(
      screen.getByLabelText('Psychique ou cognitif', { exact: false })
    ).not.toBeChecked()
    expect(screen.getByLabelText('Moteur', { exact: false })).not.toBeChecked()
    expect(screen.getByLabelText('Auditif', { exact: false })).not.toBeChecked()
    expect(
      screen.getByLabelText('Non accessible', { exact: false })
    ).not.toBeChecked()
  })

  it('should submit valid form', async () => {
    await renderAccessibility({ initialValues, onSubmit })

    const checkboxVisuel = screen.getByLabelText('Visuel', { exact: false })
    await userEvent.click(checkboxVisuel)
    await userEvent.click(await screen.findByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      {
        accessibility: {
          audio: false,
          mental: false,
          motor: false,
          none: false,
          visual: true,
        },
        offererId: '',
        subcategoryId: '',
        venueId: '',
        withdrawalDelay: '',
        withdrawalDetails: '',
        withdrawalType: '',
      },
      expect.anything()
    )
  })

  it('should check accessibilities on click', async () => {
    initialValues = {
      ...initialValues,
      accessibility: {
        [AccessiblityEnum.VISUAL]: false,
        [AccessiblityEnum.MENTAL]: false,
        [AccessiblityEnum.AUDIO]: false,
        [AccessiblityEnum.MOTOR]: false,
        [AccessiblityEnum.NONE]: false,
      },
    }
    await renderAccessibility({ initialValues, onSubmit })
    await screen.findByRole('heading', { name: 'Accessibilité' })

    const checkboxNone = screen.getByLabelText('Non accessible', {
      exact: false,
    })
    const checkboxVisuel = screen.getByLabelText('Visuel', { exact: false })
    const checkboxMental = screen.getByLabelText('Psychique ou cognitif', {
      exact: false,
    })
    const checkboxMoteur = screen.getByLabelText('Moteur', { exact: false })
    const checkboxAuditif = screen.getByLabelText('Auditif', { exact: false })

    await userEvent.click(checkboxVisuel)
    expect(checkboxVisuel).toBeChecked()
    expect(checkboxNone).not.toBeChecked()

    await userEvent.click(checkboxMental)
    expect(checkboxMental).toBeChecked()
    expect(checkboxNone).not.toBeChecked()

    await userEvent.click(checkboxMoteur)
    expect(checkboxMoteur).toBeChecked()
    expect(checkboxNone).not.toBeChecked()

    await userEvent.click(checkboxAuditif)
    expect(checkboxAuditif).toBeChecked()
    expect(checkboxNone).not.toBeChecked()

    await userEvent.click(checkboxNone)
    expect(checkboxNone).toBeChecked()
    expect(checkboxVisuel).not.toBeChecked()
    expect(checkboxMental).not.toBeChecked()
    expect(checkboxMoteur).not.toBeChecked()
    expect(checkboxAuditif).not.toBeChecked()

    await userEvent.click(checkboxAuditif)
    expect(checkboxAuditif).toBeChecked()
    expect(checkboxNone).not.toBeChecked()
  })

  it('should display an error on submit if accessibility is empty', async () => {
    initialValues = {
      ...initialValues,
      accessibility: {
        [AccessiblityEnum.VISUAL]: false,
        [AccessiblityEnum.MENTAL]: false,
        [AccessiblityEnum.AUDIO]: false,
        [AccessiblityEnum.MOTOR]: false,
        [AccessiblityEnum.NONE]: false,
      },
    }
    await renderAccessibility({ initialValues, onSubmit })

    await screen.findByRole('heading', { name: 'Accessibilité' })
    // tab to focus the first accessibility checkbox
    // then the form is touched and errors will be displayed.
    await userEvent.tab()
    await userEvent.click(await screen.findByRole('button', { name: 'Submit' }))

    expect(
      screen.getByText(
        'Veuillez sélectionner au moins un critère d’accessibilité'
      )
    ).toBeInTheDocument()
  })
})
