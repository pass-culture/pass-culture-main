import { renderHook } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'

import { OFFER_WIZARD_MODE } from 'core/Offers/constants'

import useOfferWizardMode from '../useOfferWizardMode'

const renderUseOfferWizardMode = (url: string) => {
  const wrapper = ({ children }: { children: any }) => (
    <MemoryRouter initialEntries={[url]}>{children}</MemoryRouter>
  )

  return renderHook(() => useOfferWizardMode(), {
    wrapper,
  })
}

describe('useOfferWizardMode', () => {
  it('should return mode "creation"', async () => {
    const { result } = renderUseOfferWizardMode('/test/creation/test')
    expect(result.current).toEqual(OFFER_WIZARD_MODE.CREATION)
  })

  it('should return mode "read only"', async () => {
    const { result } = renderUseOfferWizardMode('/test/test')
    expect(result.current).toEqual(OFFER_WIZARD_MODE.READ_ONLY)
  })

  it('should return mode "edition"', async () => {
    const { result } = renderUseOfferWizardMode('/test/edition/test')
    expect(result.current).toEqual(OFFER_WIZARD_MODE.EDITION)
  })
})
