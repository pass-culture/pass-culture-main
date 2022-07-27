import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import PortalContainer from '../PortalContainer'

const renderPortalContent = testId =>
  render(
    <PortalContainer>
      <div data-testid={testId}>Some content</div>
    </PortalContainer>
  )

describe('src | app | PortalContainer', () => {
  it('should mount children in DOM tree', async () => {
    renderPortalContent('portal-content')

    await expect(screen.findByTestId('portal-content')).resolves.toBeVisible()
  })

  it('should unmount children when unmounting', async () => {
    const { unmount } = renderPortalContent('portal-content')
    await unmount()

    expect(screen.queryByTestId('portal-content')).toBeNull()
  })
})
