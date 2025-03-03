import { screen, waitFor } from '@testing-library/react'
import { Formik } from 'formik'

import { StudentLevels } from 'apiClient/v1'
import { buildStudentLevelsMapWithDefaultValue } from 'commons/core/OfferEducational/utils/buildStudentLevelsMapWithDefaultValue'
import {
  RenderWithProvidersOptions,
  renderWithProviders,
} from 'commons/utils/renderWithProviders'

import { studentLevelsLabels } from './constants'
import { FormParticipants } from './FormParticipants'

const renderFormParticipants = (
  participants: Record<string, boolean>,
  isTemplate: boolean = true,
  options?: RenderWithProvidersOptions
) => {
  return renderWithProviders(
    <Formik initialValues={{ participants }} onSubmit={() => {}}>
      <FormParticipants disableForm={false} isTemplate={isTemplate} />
    </Formik>,
    options
  )
}

const featureOverrides = {
  features: ['WIP_ENABLE_MARSEILLE'],
}

describe('FormParticipants', () => {
  const participants: Record<string, boolean> = {
    ...buildStudentLevelsMapWithDefaultValue(true),
    CAPAnnee2: false,
  }

  it('should render all options with default value', async () => {
    renderFormParticipants(participants)
    expect(await screen.findAllByRole('checkbox')).toHaveLength(11)
    expect(
      screen.getByRole('checkbox', {
        name: studentLevelsLabels[StudentLevels.LYC_E_PREMI_RE],
      })
    ).toBeChecked()
  })

  it('display a new text in the "à savoir" section when marseille ff is active', async () => {
    renderFormParticipants(participants, false, featureOverrides)

    expect(
      await screen.findByText(
        'Dans le cadre du plan Marseille en Grand et du Conseil national de la refondation dans son volet éducation "Notre école, faisons-la ensemble", les écoles primaires innovantes du territoire marseillais bénéficient d’un budget pour financer des projets d’EAC avec leurs élèves.'
      )
    ).toBeInTheDocument()
  })

  it('should display new student level for MeG when ff is active', async () => {
    const participants: Record<string, boolean> =
      buildStudentLevelsMapWithDefaultValue(true, true)

    renderFormParticipants(participants, false, featureOverrides)

    expect(
      await screen.findByRole('checkbox', {
        name: 'Projet Marseille en Grand - École innovante',
      })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('checkbox', {
        name: studentLevelsLabels[StudentLevels._COLES_MARSEILLE_MATERNELLE],
      })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('checkbox', {
        name: studentLevelsLabels[StudentLevels._COLES_MARSEILLE_CP_CE1_CE2],
      })
    ).toBeInTheDocument()
    expect(
      await screen.findByRole('checkbox', {
        name: studentLevelsLabels[StudentLevels._COLES_MARSEILLE_CM1_CM2],
      })
    ).toBeInTheDocument()
  })

  it('should not display new student level for MeG when ff is not active', async () => {
    renderFormParticipants(participants, false)

    await waitFor(() => {
      expect(
        screen.queryByRole('checkbox', {
          name: 'Projet Marseille en Grand - École innovante',
        })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('checkbox', {
          name: studentLevelsLabels[StudentLevels._COLES_MARSEILLE_MATERNELLE],
        })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('checkbox', {
          name: studentLevelsLabels[StudentLevels._COLES_MARSEILLE_CP_CE1_CE2],
        })
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole('checkbox', {
          name: studentLevelsLabels[StudentLevels._COLES_MARSEILLE_CM1_CM2],
        })
      ).not.toBeInTheDocument()
    })
  })
})
