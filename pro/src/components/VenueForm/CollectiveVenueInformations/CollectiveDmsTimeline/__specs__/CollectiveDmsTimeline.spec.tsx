import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { DMSApplicationForEAC, DMSApplicationstatus } from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import * as useAnalytics from 'hooks/useAnalytics'
import { defaultCollectiveDmsApplication } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveDmsTimeline from '..'

const mockLogEvent = jest.fn()

const renderCollectiveDmsTimeline = ({
  collectiveDmsApplication,
  hasAdageId = false,
  hasAdageIdForMoreThan30Days = false,
  adageInscriptionDate = null,
  offererId = 12,
}: {
  collectiveDmsApplication: DMSApplicationForEAC
  hasAdageId?: boolean
  hasAdageIdForMoreThan30Days?: boolean
  adageInscriptionDate?: string | null
  offererId?: number
}) => {
  renderWithProviders(
    <CollectiveDmsTimeline
      collectiveDmsApplication={collectiveDmsApplication}
      hasAdageId={hasAdageId}
      hasAdageIdForMoreThan30Days={hasAdageIdForMoreThan30Days}
      adageInscriptionDate={adageInscriptionDate}
      offererId={offererId}
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
  const dmsStates = [
    DMSApplicationstatus.EN_CONSTRUCTION,
    DMSApplicationstatus.EN_INSTRUCTION,
    DMSApplicationstatus.ACCEPTE,
    DMSApplicationstatus.REFUSE,
    DMSApplicationstatus.SANS_SUITE,
  ]
  beforeEach(() => {
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useAnalytics'),
      logEvent: mockLogEvent,
    }))
  })
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

  it.each(dmsStates)(
    'should log event on click dms link',
    async (dmsState: DMSApplicationstatus) => {
      renderCollectiveDmsTimeline({
        collectiveDmsApplication: {
          ...defaultCollectiveDmsApplication,
          state: dmsState,
        },
      })
      const dmsLink = screen.getByRole('link', {
        name: 'Consulter ma messagerie sur Démarches Simplifiées',
      })
      await userEvent.click(dmsLink)
      expect(mockLogEvent).toHaveBeenCalledWith(Events.CLICKED_EAC_DMS_LINK, {
        from: '/',
        dmsApplicationStatus: dmsState,
      })
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
