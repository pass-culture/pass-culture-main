import { render, screen } from '@testing-library/react'

import { FieldEnum } from '@/apiClient/v1'

import {
  HasCapability,
  hasCapability,
  OfferCapabilityProvider,
} from './offerCapabilityContext'

describe('hasCapability', () => {
  it('should return whether the capability is in the list', () => {
    expect(hasCapability([FieldEnum.TITLE, FieldEnum.EAN], FieldEnum.EAN)).toBe(
      true
    )
    expect(
      hasCapability([FieldEnum.TITLE, FieldEnum.EAN], FieldEnum.AUTHOR)
    ).toBe(false)
  })
})

describe('HasCapability', () => {
  it('should render children when the capability is present', () => {
    render(
      <OfferCapabilityProvider capabilities={[FieldEnum.TITLE, FieldEnum.EAN]}>
        <HasCapability name={FieldEnum.EAN}>
          <span>EAN field</span>
        </HasCapability>
      </OfferCapabilityProvider>
    )

    expect(screen.getByText('EAN field')).toBeInTheDocument()
  })

  it('should not render children when the capability is missing', () => {
    render(
      <OfferCapabilityProvider capabilities={[FieldEnum.TITLE]}>
        <HasCapability name={FieldEnum.AUTHOR}>
          <span>Author field</span>
        </HasCapability>
      </OfferCapabilityProvider>
    )

    expect(screen.queryByText('Author field')).not.toBeInTheDocument()
  })

  it('should not render children without provider', () => {
    render(
      <HasCapability name={FieldEnum.TITLE}>
        <span>Title field</span>
      </HasCapability>
    )

    expect(screen.queryByText('Title field')).not.toBeInTheDocument()
  })
})
