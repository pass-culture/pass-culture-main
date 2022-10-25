import '@testing-library/jest-dom'
import { renderHook } from '@testing-library/react-hooks'
import React from 'react'
import { MemoryRouter } from 'react-router'

import { OFFER_WIZARD_MODE } from 'core/Offers'

import useOfferWizardMode from '../useOfferWizardMode'

const renderUseOfferWizardMode = ({ url }: { url: string }) => {
  const wrapper = ({ children }: { children: any }) => (
    <MemoryRouter initialEntries={[url]}>{children}</MemoryRouter>
  )

  return renderHook(() => useOfferWizardMode(), {
    wrapper,
  })
}

describe('useOfferWizardMode', () => {
  it('should return mode "creation"', async () => {
    const { result } = renderUseOfferWizardMode({
      url: 'test/creation/test',
    })
    expect(result.current).toEqual(OFFER_WIZARD_MODE.CREATION)
  })
  it('should return mode "creation"', async () => {
    const { result } = renderUseOfferWizardMode({
      url: 'test/brouillon/test',
    })
    expect(result.current).toEqual(OFFER_WIZARD_MODE.DRAFT)
  })
  it('should return mode "creation"', async () => {
    const { result } = renderUseOfferWizardMode({
      url: 'test/test',
    })
    expect(result.current).toEqual(OFFER_WIZARD_MODE.EDITION)
  })
})
