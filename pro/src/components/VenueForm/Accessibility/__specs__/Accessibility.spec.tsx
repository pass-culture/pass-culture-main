import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'
import * as yup from 'yup'

import { VenueFormValues } from 'components/VenueForm'
import { AccessiblityEnum } from 'core/shared'
import { SubmitButton } from 'ui-kit'

import { Accessibility, validationSchema } from '..'

const renderAccessibility = ({
  initialValues,
  isCreatingVenue,
  onSubmit = jest.fn(),
}: {
  initialValues: Partial<VenueFormValues>
  isCreatingVenue: boolean
  onSubmit: () => void
}) => {
  return render(
    <Formik
      initialValues={initialValues}
      onSubmit={onSubmit}
      validationSchema={yup.object().shape(validationSchema)}
    >
      <Form>
        <Accessibility isCreatingVenue={isCreatingVenue} />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )
}

describe('Accessibility', () => {
  let initialValues: Partial<VenueFormValues>
  let isCreatingVenue: boolean
  const onSubmit = jest.fn()

  beforeEach(() => {
    initialValues = {
      isVenueVirtual: false,
      accessibility: {
        [AccessiblityEnum.VISUAL]: false,
        [AccessiblityEnum.MENTAL]: false,
        [AccessiblityEnum.AUDIO]: false,
        [AccessiblityEnum.MOTOR]: false,
        [AccessiblityEnum.NONE]: false,
      },
    }
    isCreatingVenue = true
  })

  it('should display initial component', async () => {
    await renderAccessibility({ initialValues, isCreatingVenue, onSubmit })

    expect(
      await screen.findByRole('heading', { name: 'Accessibilité du lieu' })
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Ce lieu est accessible au public en situation de handicap :'
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
    await renderAccessibility({
      initialValues,
      isCreatingVenue,
      onSubmit,
    })

    const checkboxVisuel = screen.getByLabelText('Visuel', { exact: false })
    await userEvent.click(checkboxVisuel)
    await userEvent.click(await screen.findByText('Submit'))

    expect(onSubmit).toHaveBeenCalledWith(
      {
        isVenueVirtual: false,
        accessibility: {
          audio: false,
          mental: false,
          motor: false,
          none: false,
          visual: true,
        },
      },
      expect.anything()
    )
  })

  it('should check accessibilities on click', async () => {
    await renderAccessibility({ initialValues, isCreatingVenue, onSubmit })

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

  it('should display an error on submit if accessibility is empty for non virtual venues', async () => {
    await renderAccessibility({ initialValues, isCreatingVenue, onSubmit })

    // tab to focus the first accessibility checkbox
    // then the form is touched and errors will be displayed.
    await userEvent.tab()
    await userEvent.click(await screen.findByRole('button', { name: 'Submit' }))

    expect(
      await screen.findByText(
        'Veuillez sélectionner au moins un critère d’accessibilité'
      )
    ).toBeInTheDocument()
  })

  it('should not display an error on submit if accessibility is empty for virtual venues', async () => {
    initialValues.isVenueVirtual = true
    await renderAccessibility({ initialValues, isCreatingVenue, onSubmit })

    // tab to focus the first accessibility checkbox
    // then the form is touched and errors will be displayed.
    await userEvent.tab()
    await userEvent.click(await screen.findByRole('button', { name: 'Submit' }))

    expect(
      screen.queryByText(
        'Veuillez sélectionner au moins un critère d’accessibilité'
      )
    ).not.toBeInTheDocument()
  })

  it('should display apply accessibility to all offer when its venue edition and accessibility has changed', async () => {
    isCreatingVenue = false
    initialValues = {
      accessibility: {
        [AccessiblityEnum.VISUAL]: false,
        [AccessiblityEnum.MENTAL]: false,
        [AccessiblityEnum.AUDIO]: false,
        [AccessiblityEnum.MOTOR]: false,
        [AccessiblityEnum.NONE]: true,
      },
    }
    await renderAccessibility({ initialValues, isCreatingVenue, onSubmit })
    const checkboxVisuel = screen.getByLabelText('Visuel', { exact: false })

    await userEvent.click(checkboxVisuel)
    expect(
      await screen.findByLabelText(
        'Appliquer le changement à toutes les offres existantes'
      )
    ).toBeInTheDocument()
  })
})
