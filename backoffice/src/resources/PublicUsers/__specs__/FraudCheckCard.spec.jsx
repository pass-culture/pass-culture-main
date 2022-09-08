import '@testing-library/jest-dom'

import { fireEvent, render, screen, waitFor } from '@testing-library/react'

import { FraudCheckCard } from '../Components/FraudCheckCard'
import { PublicUserRolesEnum } from '../types'

const renderFraudCheckCard = props => render(<FraudCheckCard {...props} />)

const someFraudCheck = {
  type: 'UBBLE',
  thirdPartyId: 'some-third-party-id',
  dateCreated: new Date(),
  status: 'ok',
}

const fraudCheckTechnicalDetailsId = 'fraudCheckTechnicalDetails'

describe('fraud check card', () => {
  it('should display fraud check information', () => {
    // Given
    const dateCreated = new Date('2022-08-11T12:10:22Z')

    const fraudCheckWithValidDate = {
      ...someFraudCheck,
      dateCreated: dateCreated,
    }
    const props = {
      eligibilityFraudCheck: {
        role: PublicUserRolesEnum.underageBeneficiary,
        items: [fraudCheckWithValidDate],
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
    expect(
      screen.getByText(fraudCheckWithValidDate.thirdPartyId)
    ).toBeInTheDocument()
    expect(screen.getByTestId(statusIconTestId)).toBeInTheDocument()
    expect(screen.getByTestId(fraudCheckTechnicalDetailsId)).not.toBeVisible()
    expect(screen.getByText('11/08/2022 à 12:10:22')).toBeInTheDocument()
  })

  it('should display fraud check information with empty creation date', () => {
    // Given
    const dateCreated = null

    const fraudCheckWithInvalidDate = {
      ...someFraudCheck,
      dateCreated: dateCreated,
    }
    const props = {
      eligibilityFraudCheck: {
        role: PublicUserRolesEnum.underageBeneficiary,
        items: [fraudCheckWithInvalidDate],
      },
    }

    const fraudCheckCreationDate = 'fraudCheckCreationDate'

    // When
    renderFraudCheckCard(props)

    // Then
    expect(screen.getByTestId(fraudCheckCreationDate)).toBeInTheDocument()
    expect(screen.getByTestId(fraudCheckCreationDate)).toBeEmptyDOMElement()
  })

  it('should display fraud check information with bad formated creation date', () => {
    // Given
    const badDateAsString = 'not-a-valid-date'
    const dateCreated = new Date(badDateAsString)

    const fraudCheckWithInvalidDate = {
      ...someFraudCheck,
      dateCreated: dateCreated,
    }
    const props = {
      eligibilityFraudCheck: {
        role: PublicUserRolesEnum.underageBeneficiary,
        items: [fraudCheckWithInvalidDate],
      },
    }
    const fraudCheckCreationDate = 'fraudCheckCreationDate'

    // When
    renderFraudCheckCard(props)

    // Then
    expect(screen.getByTestId(fraudCheckCreationDate)).toBeInTheDocument()
    expect(screen.getByTestId(fraudCheckCreationDate)).toBeEmptyDOMElement()
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
