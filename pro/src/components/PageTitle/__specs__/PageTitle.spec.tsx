import { render } from '@testing-library/react'
import React from 'react'

import PageTitle from '../PageTitle'

describe('pageTitle', () => {
  it('should override document title', () => {
    render(<PageTitle title="My title" />)

    expect(document.title).toBe('My title - pass Culture Pro')
  })

  it('should set default document title on unmount', () => {
    const { unmount } = render(<PageTitle title="My title" />)

    unmount()

    expect(document.title).toBe('pass Culture Pro')
  })
})
