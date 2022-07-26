import '@testing-library/jest-dom'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import { FraudCheckCard } from '../Components/FraudCheckCard'
import { PublicUserRolesEnum } from '../types'

const renderFraudCheckCard = props => render(<FraudCheckCard {...props} />)
const someFraudCheck = {
  type: 'UBBLE',
  thirdPartyId: 'some-third-party-id',
  dateCreated: Date(),
  status: 'ok',
}

const fraudCheckTechnicalDetailsId = 'fraudCheckTechnicalDetails'

describe('fraud check card', () => {
  it('should display fraud check information', () => {
    // Given
    const props = {
      eligibilityFraudCheck: {
        role: PublicUserRolesEnum.underageBeneficiary,
        items: [someFraudCheck],
      },
    }
    const expectedLabel = 'UBBLE'
    const expectedBadgeText = 'Pass 15-17'
    const statusIconTestId = 'CheckCircleOutlineIcon'

    // When
    renderFraudCheckCard(props)

    // Then
    expect(screen.getByText(expectedLabel)).toBeInTheDocument()
    expect(screen.getByText(expectedBadgeText)).toBeInTheDocument()
    expect(screen.getByText(someFraudCheck.thirdPartyId)).toBeInTheDocument()
    expect(screen.getByTestId(statusIconTestId)).toBeInTheDocument()
    expect(screen.getByTestId(fraudCheckTechnicalDetailsId)).not.toBeVisible()
  })

  it('should reveal technical details when dedicated switch is on', () => {
    // Given
    const technicalDetails = 'some-technical-detail'
    const props = {
      eligibilityFraudCheck: {
        role: PublicUserRolesEnum.underageBeneficiary,
        items: [
          {
            ...someFraudCheck,
            technicalDetails: technicalDetails,
          },
        ],
      },
    }

    // When
    renderFraudCheckCard(props)
    fireEvent.click(screen.getByRole('checkbox'))

    // Then
    expect(screen.getByTestId(fraudCheckTechnicalDetailsId)).toBeVisible()
    expect(screen.getByText(`"${technicalDetails}"`)).toBeInTheDocument()
  })
})
