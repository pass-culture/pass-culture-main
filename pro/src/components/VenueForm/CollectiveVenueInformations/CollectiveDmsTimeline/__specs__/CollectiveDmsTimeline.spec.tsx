import { render, screen } from '@testing-library/react'
import React from 'react'

import { DMSApplicationForEAC } from 'apiClient/v1'
import { defaultCollectiveDmsApplication } from 'utils/collectiveApiFactories'
import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveDmsTimeline from '..'
import { DMS_STATUS } from '../CollectiveDmsTimeline'

const renderCollectiveDmsTimeline = ({
  collectiveDmsApplication,
}: {
  collectiveDmsApplication: DMSApplicationForEAC
}) => {
  renderWithProviders(
    <CollectiveDmsTimeline
      collectiveDmsApplication={collectiveDmsApplication}
    />
  )
}

interface ITestCaseProps {
  collectiveDmsApplication: DMSApplicationForEAC
  expectedLabel: string
}

describe('CollectiveDmsTimeline', () => {
  const testCases: ITestCaseProps[] = [
    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMS_STATUS.DRAFT,
      },
      expectedLabel: 'Déposez votre demande de référencement',
    },
    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMS_STATUS.SUBMITTED,
      },
      expectedLabel: 'Votre dossier a été déposé',
    },
    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMS_STATUS.INSTRUCTION,
      },
      expectedLabel: "Votre dossier est en cours d'instruction",
    },
    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMS_STATUS.ADD_IN_ADAGE,
      },
      expectedLabel: 'Votre demande de référencement a été acceptée',
    },

    {
      collectiveDmsApplication: {
        ...defaultCollectiveDmsApplication,
        state: DMS_STATUS.ADDED_IN_ADAGE,
      },
      expectedLabel:
        'Votre lieu a été ajouté dans ADAGE par le Ministère de l’Education Nationale',
    },
  ]
  it.each(testCases)(
    'should render %s status',
    ({ collectiveDmsApplication, expectedLabel }) => {
      renderCollectiveDmsTimeline({ collectiveDmsApplication })
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    }
  )

  it('should throw error if dms status doesnt exist', () => {
    expect(() =>
      render(
        <CollectiveDmsTimeline
          collectiveDmsApplication={{
            ...defaultCollectiveDmsApplication,
            state: 'NOT_EXISTING_STATUS',
          }}
        />
      )
    ).toThrowError()
  })
})
