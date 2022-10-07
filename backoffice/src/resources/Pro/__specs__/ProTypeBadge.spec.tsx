import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

import { ProTypeBadge, ProTypeBadgeProps } from '../Components/ProTypeBadge'
import { ProTypeEnum } from '../types'

const renderProTypeBadge = (props: ProTypeBadgeProps) => {
  return render(<ProTypeBadge {...props} />)
}

describe('Pro Type Badge', () => {
  it('should display the status badge for an offerer', () => {
    //Given
    const proType = ProTypeEnum.offerer

    const proResult = {
      id: 1232132132332,
      payload: {},
      resourceType: proType,
    }

    const props = {
      type: proType,
      resource: proResult,
    }

    const expectedText = 'Structure'

    //When
    renderProTypeBadge(props)

    //Then
    expect(screen.getByText(expectedText)).toBeInTheDocument()
  })
  it('should display the status badge for a non-permanent venue', () => {
    //Given
    const proType = ProTypeEnum.venue

    const proResult = {
      id: 1232132132332,
      payload: {
        permanent: false,
      },
      resourceType: proType,
    }

    const props = {
      type: proType,
      resource: proResult,
    }

    const expectedText = 'Lieu Non-Permanent'
    //When
    renderProTypeBadge(props)

    //Then
    expect(screen.getByText(expectedText)).toBeInTheDocument()
  })
})
