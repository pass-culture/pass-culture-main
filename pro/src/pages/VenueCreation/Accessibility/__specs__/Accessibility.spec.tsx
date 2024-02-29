import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import { AccessiblityEnum } from 'core/shared'
import { VenueCreationFormValues } from 'pages/VenueCreation/types'
import { SubmitButton } from 'ui-kit'

import { Accessibility } from '../Accessibility'

const renderAccessibility = ({
  initialValues,
  isCreatingVenue,
  onSubmit = vi.fn(),
}: {
  initialValues: Partial<VenueCreationFormValues>
  isCreatingVenue: boolean
  onSubmit: () => void
}) => {
  return render(
    <Formik initialValues={initialValues} onSubmit={onSubmit}>
      <Form>
        <Accessibility isCreatingVenue={isCreatingVenue} />
        <SubmitButton isLoading={false}>Submit</SubmitButton>
      </Form>
    </Formik>
  )
}

describe('Accessibility', () => {
  let initialValues: Partial<VenueCreationFormValues>
  let isCreatingVenue: boolean
  const onSubmit = vi.fn()

  beforeEach(() => {
    initialValues = {
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
    renderAccessibility({ initialValues, isCreatingVenue, onSubmit })

    expect(
      await screen.findByRole('heading', { name: 'Critères d’accessibilité' })
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Ce lieu est accessible au public en situation de handicap : *'
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
    renderAccessibility({ initialValues, isCreatingVenue, onSubmit })

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
      },
      expect.anything()
    )
  })

  it('should check accessibilities on click', async () => {
    renderAccessibility({ initialValues, isCreatingVenue, onSubmit })

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
    renderAccessibility({ initialValues, isCreatingVenue, onSubmit })
    const checkboxVisuel = screen.getByLabelText('Visuel', { exact: false })

    await userEvent.click(checkboxVisuel)
    expect(
      await screen.findByLabelText(
        'Appliquer le changement à toutes les offres existantes'
      )
    ).toBeInTheDocument()
  })
})
