import { screen } from '@testing-library/react'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import CollectiveDmsTimeline from '..'
import { DMS_STATUS } from '../CollectiveDmsTimeline'

const renderCollectiveDmsTimeline = ({
  collectiveDmsStatus,
}: {
  collectiveDmsStatus: string
}) => {
  renderWithProviders(
    <CollectiveDmsTimeline collectiveDmsStatus={collectiveDmsStatus} />
  )
}

interface ITestCaseProps {
  collectiveDmsStatus: string
  expectedLabel: string
}

describe('CollectiveDmsTimeline', () => {
  const testCases: ITestCaseProps[] = [
    {
      collectiveDmsStatus: DMS_STATUS.DRAFT,
      expectedLabel: 'Déposez votre demande de référencement',
    },
    {
      collectiveDmsStatus: DMS_STATUS.SUBMITTED,
      expectedLabel: 'Votre dossier a été déposé',
    },
    {
      collectiveDmsStatus: DMS_STATUS.INSTRUCTION,
      expectedLabel: "Votre dossier est en cours d'instruction",
    },
    {
      collectiveDmsStatus: DMS_STATUS.ADD_IN_ADAGE,
      expectedLabel: 'Votre demande de référencement a été acceptée',
    },

    {
      collectiveDmsStatus: DMS_STATUS.ADDED_IN_ADAGE,
      expectedLabel:
        'Votre lieu a été ajouté dans ADAGE par le Ministère de l’Education Nationale',
    },
  ]
  it.each(testCases)(
    'should render %s status',
    ({ collectiveDmsStatus, expectedLabel }) => {
      renderCollectiveDmsTimeline({ collectiveDmsStatus })
      expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    }
  )
})
