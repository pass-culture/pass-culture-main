import { screen } from '@testing-library/react'
import React from 'react'

import { DMSApplicationForEAC, DMSApplicationstatus } from 'apiClient/v1'
import { defaultCollectiveDmsApplication } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveDmsTimeline from '..'

const renderCollectiveDmsTimeline = ({
  collectiveDmsApplication,
  hasAdageId = false,
  hasAdageIdForMoreThan30Days = false,
}: {
  collectiveDmsApplication: DMSApplicationForEAC
  hasAdageId?: boolean
  hasAdageIdForMoreThan30Days?: boolean
}) => {
  renderWithProviders(
    <CollectiveDmsTimeline
      collectiveDmsApplication={collectiveDmsApplication}
      hasAdageId={hasAdageId}
      hasAdageIdForMoreThan30Days={hasAdageIdForMoreThan30Days}
    />
  )
}

interface ITestCaseProps {
  collectiveDmsApplication: DMSApplicationForEAC
  hasAdageId?: boolean
  hasAdageIdForMoreThan30Days?: boolean
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
    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.ACCEPTE,
      },
      hasAdageId: true,
      hasAdageIdForMoreThan30Days: true,
      expectedLabel: 'Ce lieu est référencé sur ADAGE',
    },
  ]
  it.each(testCases)(
    'should render %s status',
    ({
      collectiveDmsApplication,
      hasAdageId,
      hasAdageIdForMoreThan30Days,
      expectedLabel,
    }) => {
      renderCollectiveDmsTimeline({
        collectiveDmsApplication,
        hasAdageId,
        hasAdageIdForMoreThan30Days,
      })
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    }
  )
})
