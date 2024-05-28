import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { Form, Formik } from 'formik'
import React from 'react'

import { AccessibilityEnum } from 'core/shared/types'
import { VenueCreationFormValues } from 'pages/VenueCreation/types'
import { Button } from 'ui-kit/Button/Button'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'utils/renderWithProviders'

import { Accessibility, AccessiblityProps } from '../Accessibility'

const onSubmit = vi.fn()

const renderAccessibility = (
  initialValues: Partial<VenueCreationFormValues>,
  props: Partial<AccessiblityProps> = {},
  overrides: RenderWithProvidersOptions = {}
) => {
  return renderWithProviders(
    <Formik initialValues={initialValues} onSubmit={onSubmit}>
      <Form>
        <Accessibility isCreatingVenue={false} {...props} />
        <Button type="submit" isLoading={false}>
          Submit
        </Button>
      </Form>
    </Formik>,
    overrides
  )
}

describe('Accessibility', () => {
  let initialValues: Partial<VenueCreationFormValues>

  beforeEach(() => {
    initialValues = {
      accessibility: {
        [AccessibilityEnum.VISUAL]: false,
        [AccessibilityEnum.MENTAL]: false,
        [AccessibilityEnum.AUDIO]: false,
        [AccessibilityEnum.MOTOR]: false,
        [AccessibilityEnum.NONE]: false,
      },
    }
  })

  it('should display initial component', async () => {
    renderAccessibility(initialValues, { isCreatingVenue: true })

    expect(
      await screen.findByRole('heading', { name: 'Modalités d’accessibilité' })
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        'Votre établissement est accessible au public en situation de handicap : *'
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
    renderAccessibility(initialValues, { isCreatingVenue: true })

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
    renderAccessibility(initialValues, { isCreatingVenue: true })

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
    initialValues = {
      accessibility: {
        [AccessibilityEnum.VISUAL]: false,
        [AccessibilityEnum.MENTAL]: false,
        [AccessibilityEnum.AUDIO]: false,
        [AccessibilityEnum.MOTOR]: false,
        [AccessibilityEnum.NONE]: true,
      },
    }
    renderAccessibility(initialValues, { isCreatingVenue: false })
    const checkboxVisuel = screen.getByLabelText('Visuel', { exact: false })

    await userEvent.click(checkboxVisuel)
    expect(
      await screen.findByLabelText(
        'Appliquer le changement à toutes les offres existantes'
      )
    ).toBeInTheDocument()
  })

  it('should display the acces libre callout in edition', () => {
    renderAccessibility(initialValues, {
      isCreatingVenue: false,
      isVenuePermanent: true,
    })

    expect(
      screen.getByText(
        'Renseignez facilement les modalités d’accessibilité de votre établissement sur la plateforme collaborative acceslibre.beta.gouv.fr'
      )
    ).toBeInTheDocument()
  })

  it('should not display the acces libre callout in edition for non permanent venues', () => {
    renderAccessibility(initialValues, {
      isCreatingVenue: false,
      isVenuePermanent: false,
    })

    expect(
      screen.queryByText(
        'Renseignez facilement les modalités d’accessibilité de votre établissement sur la plateforme collaborative acceslibre.beta.gouv.fr'
      )
    ).not.toBeInTheDocument()
  })

  it('should not display the acces libre callout in creation', () => {
    renderAccessibility(initialValues, { isCreatingVenue: true })

    expect(
      screen.queryByText(
        'Renseignez facilement les modalités d’accessibilité de votre établissement sur la plateforme collaborative acceslibre.beta.gouv.fr'
      )
    ).not.toBeInTheDocument()
  })
})
