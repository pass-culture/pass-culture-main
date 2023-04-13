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
  adageInscriptionDate = null,
}: {
  collectiveDmsApplication: DMSApplicationForEAC
  hasAdageId?: boolean
  hasAdageIdForMoreThan30Days?: boolean
  adageInscriptionDate?: string | null
}) => {
  renderWithProviders(
    <CollectiveDmsTimeline
      collectiveDmsApplication={collectiveDmsApplication}
      hasAdageId={hasAdageId}
      hasAdageIdForMoreThan30Days={hasAdageIdForMoreThan30Days}
      adageInscriptionDate={adageInscriptionDate}
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
    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.EN_CONSTRUCTION,
      },
      hasAdageId: true,
      expectedLabel: 'Ce lieu est référencé sur ADAGE',
    },
    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMSApplicationstatus.SANS_SUITE,
      },
      expectedLabel: 'Votre demande de référencement a été classée sans suite',
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

  it('should display dates for status', () => {
    const collectiveDmsApplication = {
      application: 11922836,
      buildDate: '2023-03-23T15:08:35Z',
      depositDate: '2024-03-23T15:08:33Z',
      lastChangeDate: '2023-03-26T15:08:35Z',
      instructionDate: '2025-03-24T15:08:33Z',
      processingDate: '2025-03-27T15:08:33Z',
      procedure: 123,
      state: DMSApplicationstatus.ACCEPTE,
      venueId: 33,
    }

    renderCollectiveDmsTimeline({
      collectiveDmsApplication: collectiveDmsApplication,
      hasAdageId: true,
      hasAdageIdForMoreThan30Days: false,
      adageInscriptionDate: '2025-03-28T15:08:33Z',
    })

    expect(screen.getByText(/23 mars 2023/)).toBeInTheDocument()
    expect(screen.getByText(/24 mars 2025/)).toBeInTheDocument()
    expect(screen.getByText(/27 mars 2025/)).toBeInTheDocument()
    expect(screen.getByText(/28 mars 2025/)).toBeInTheDocument()
  })
})
