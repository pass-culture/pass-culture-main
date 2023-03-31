import { screen } from '@testing-library/react'
import React from 'react'

import { DMSApplicationForEAC, DMSApplicationstatus } from 'apiClient/v1'
import { defaultCollectiveDmsApplication } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveDmsTimeline from '..'

const renderCollectiveDmsTimeline = ({
  collectiveDmsApplication,
  hasAdageId = false,
}: {
  collectiveDmsApplication: DMSApplicationForEAC
  hasAdageId?: boolean
}) => {
  renderWithProviders(
    <CollectiveDmsTimeline
      collectiveDmsApplication={collectiveDmsApplication}
      hasAdageId={hasAdageId}
    />
  )
}

interface ITestCaseProps {
  collectiveDmsApplication: DMSApplicationForEAC
  hasAdageId?: boolean
  expectedLabel: string
}

describe('CollectiveDmsTimeline', () => {
  const testCases: ITestCaseProps[] = [
    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.EN_CONSTRUCTION,
      },
      expectedLabel: 'Votre dossier a été déposé',
    },
    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.EN_INSTRUCTION,
      },
      expectedLabel: "Votre dossier est en cours d'instruction",
    },
    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.ACCEPTE,
      },
      expectedLabel: 'Votre demande de référencement a été acceptée',
    },

    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.ACCEPTE,
      },
      hasAdageId: true,
      expectedLabel:
        'Votre lieu a été ajouté dans ADAGE par le Ministère de l’Education Nationale',
    },
    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.REFUSE,
      },
      expectedLabel: 'Votre demande de référencement a été refusée',
    },
  ]
  it.each(testCases)(
    'should render %s status',
    ({ collectiveDmsApplication, hasAdageId, expectedLabel }) => {
      renderCollectiveDmsTimeline({ collectiveDmsApplication, hasAdageId })
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    }
  )
})
