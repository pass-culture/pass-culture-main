import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'

import { ManualReviewModal } from '../Components/ManualReviewModal'
import {
  FraudCheckStatus,
  FraudCheckType,
  UserRole,
} from '../../../TypesFromApi'

const renderManualReviewModal = props =>
  render(<ManualReviewModal {...props} />)
const someUser = {
  id: 123,
  lastname: 'Durond',
  firstname: 'Laurent',
  isActive: true,
  roles: [UserRole.BENEFICIARY],
  email: 'laurentdurond@example.com',
  dateOfBirth: new Date(2005, 12, 25),
}

describe('manual review modal button', () => {
  it('should be disabled when beneficiary has no fraud check', () => {
    // Given
    const eligibilityFraudCheck = {
      idCheckHistory: [],
      subscriptionItems: [],
    }
    const props = {
      user: someUser,
      eligibilityFraudChecks: eligibilityFraudCheck,
    }
    const expectedLabel =
      'Revue manuelle non disponible (aucun fraud check avec nom, prénom, date de naissance)'

    // When
    renderManualReviewModal(props)

    // Then
    expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('should be active when user has fraud check', () => {
    // Given
    const fraudCheck = {
      type: FraudCheckType.Ubble,
      thirdPartyId: 'some-id',
      dateCreated: new Date(2022, 7, 11),
      status: FraudCheckStatus.Ok,
    }
    const eligibilityFraudCheck = {
      subscriptionItems: [],
      idCheckHistory: [fraudCheck],
    }
    const props = {
      user: someUser,
      eligibilityFraudChecks: eligibilityFraudCheck,
    }
    const expectedLabel = 'Revue manuelle'

    // When
    renderManualReviewModal(props)

    // Then
    expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    expect(screen.getByRole('button')).toBeEnabled()
  })
})
