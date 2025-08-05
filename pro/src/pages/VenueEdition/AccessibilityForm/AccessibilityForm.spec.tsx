import { screen, waitFor } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { AccessibilityFormValues } from 'commons/core/shared/types'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'
import { VenueEditionFormValues } from 'pages/VenueEdition/types'
import { FormProvider, useForm } from 'react-hook-form'
import { Button } from 'ui-kit/Button/Button'

import { AccessibilityForm, AccessiblityFormProps } from './AccessibilityForm'

const onSubmit = vi.fn()

const MOCK_DATA = {
  externalAccessibilityId: '123',
  externalAccessibilityData: {
    isAccessibleAudioDisability: true,
    isAccessibleMentalDisability: false,
    isAccessibleMotorDisability: true,
    isAccessibleVisualDisability: true,
    motorDisability: {
      facilities: 'Sanitaire adapté',
      exterior: 'Non renseigné',
      entrance: 'Non renseigné',
      parking: "Stationnement adapté dans l'établissement",
    },
    audioDisability: {
      deafAndHardOfHearing: ['boucle à induction magnétique fixe'],
    },
    visualDisability: {
      soundBeacon: 'Non renseigné',
      audioDescription: [
        'avec équipement permanent, casques et boîtiers disponibles à l’accueil',
      ],
    },
    mentalDisability: {
      trainedPersonnel: 'Personnel non sensibilisé / formé',
    },
  },
}

const LABELS = {
  internal: {
    title: 'Modalités d’accessibilité',
    calloutLabel: 'Aller sur acceslibre.beta.gouv.fr',
    checkboxLabels: {
      visual: 'Visuel',
      mental: 'Psychique ou cognitif',
      motor: 'Moteur',
      audio: 'Auditif',
      none: 'Non accessible',
    },
  },
  external: {
    title: 'Modalités d’accessibilité via acceslibre',
    calloutLabel: 'Éditer sur acceslibre',
    collapsibleSectionTitles: [
      'Handicap moteur',
      'Handicap cognitif',
      'Handicap auditif',
      'Handicap visuel',
    ],
  },
}

function renderAccessibility(
  initialValues: Partial<VenueEditionFormValues>,
  props: AccessiblityFormProps,
  overrides: RenderWithProvidersOptions = {}
) {
  const Wrapper = () => {
    const methods = useForm({
      defaultValues: initialValues,
    })

    return (
      <FormProvider {...methods}>
        <form onSubmit={methods.handleSubmit(onSubmit)}>
          <AccessibilityForm {...props} />
          <Button type="submit" isLoading={false}>
            Submit
          </Button>
        </form>
      </FormProvider>
    )
  }

  return renderWithProviders(<Wrapper />, overrides)
}

describe('Accessibility', () => {
  it('should not render a callout when venue is not permanent', () => {
    renderAccessibility(
      {
        accessibility: {} as AccessibilityFormValues,
      },
      {
        isVenuePermanent: false,
        externalAccessibilityId: null,
        externalAccessibilityData: null,
      }
    )

    const callout = screen.queryByTestId('accessibility-callout')
    expect(callout).not.toBeInTheDocument()
  })

  describe('when accessibility is defined via acceslibre', () => {
    it('should render an appropriate title and callout', () => {
      renderAccessibility(
        {
          accessibility: {} as AccessibilityFormValues,
        },
        {
          isVenuePermanent: true,
          externalAccessibilityId: MOCK_DATA.externalAccessibilityId,
          externalAccessibilityData: MOCK_DATA.externalAccessibilityData,
        }
      )

      expect(screen.getByText(LABELS.external.title)).toBeInTheDocument()
      expect(screen.getByText(LABELS.external.calloutLabel)).toBeInTheDocument()
    })

    it('should render collapsible sections for external accessibility', () => {
      renderAccessibility(
        {
          accessibility: {} as AccessibilityFormValues,
        },
        {
          isVenuePermanent: true,
          externalAccessibilityId: MOCK_DATA.externalAccessibilityId,
          externalAccessibilityData: MOCK_DATA.externalAccessibilityData,
        }
      )

      LABELS.external.collapsibleSectionTitles.forEach((title) => {
        expect(screen.getByText(title)).toBeInTheDocument
      })
    })
  })

  describe('when accessibility is not defined via acceslibre', () => {
    it('should render an appropriate title and callout', () => {
      renderAccessibility(
        {
          accessibility: {} as AccessibilityFormValues,
        },
        {
          isVenuePermanent: true,
          externalAccessibilityId: null,
          externalAccessibilityData: null,
        }
      )

      expect(screen.getByText(LABELS.internal.title)).toBeInTheDocument()
      expect(screen.getByText(LABELS.internal.calloutLabel)).toBeInTheDocument()
    })

    it('should render internal accessibility checkboxes', () => {
      renderAccessibility(
        {
          accessibility: {} as AccessibilityFormValues,
        },
        {
          isVenuePermanent: true,
          externalAccessibilityId: null,
          externalAccessibilityData: null,
        }
      )

      Object.entries(LABELS.internal.checkboxLabels).forEach(([, label]) => {
        expect(screen.getByText(label)).toBeInTheDocument()
      })
    })

    it('should render an extra checkbox to apply change on all offers when one is checked', async () => {
      const initialValues = {
        accessibility: {
          none: true,
          visual: false,
          mental: false,
          motor: false,
          audio: false,
        },
      }

      renderAccessibility(initialValues, {
        isVenuePermanent: true,
        externalAccessibilityId: null,
        externalAccessibilityData: null,
      })

      const visualCheckbox = screen.getByLabelText(
        LABELS.internal.checkboxLabels.visual
      )
      await userEvent.click(visualCheckbox)

      await waitFor(() => {
        const allOffersCheckbox = screen.getByLabelText(
          'Appliquer le changement à toutes les offres existantes'
        )
        expect(allOffersCheckbox).toBeInTheDocument()
      })
    })

    it('should submit the form when the submit button is clicked', async () => {
      const initialValues = {
        accessibility: {
          none: true,
          visual: false,
          mental: false,
          motor: false,
          audio: false,
        },
      }

      renderAccessibility(initialValues, {
        isVenuePermanent: true,
        externalAccessibilityId: null,
        externalAccessibilityData: null,
      })

      const changedValues = { ...initialValues }
      const changedCheckboxes: Array<
        keyof typeof LABELS.internal.checkboxLabels
      > = ['mental', 'motor']
      for (const checkbox of changedCheckboxes) {
        changedValues.accessibility[checkbox] =
          !initialValues.accessibility[checkbox]

        if (changedValues.accessibility[checkbox]) {
          changedValues.accessibility.none = false
        }

        const checkboxElement = screen.getByLabelText(
          LABELS.internal.checkboxLabels[checkbox]
        )
        await userEvent.click(checkboxElement)
      }

      const submitButton = screen.getByText('Submit')
      await userEvent.click(submitButton)

      expect(onSubmit).toHaveBeenCalledWith(changedValues, expect.anything())
    })
  })
})
