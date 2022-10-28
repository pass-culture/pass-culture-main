import { render } from '@testing-library/react'
import React from 'react'

import PageTitle from '../PageTitle'

describe('pageTitle', () => {
  it('should override document title', () => {
    // When
    render(<PageTitle title="My title" />)

    // Then
    expect(document.title).toBe('My title - pass Culture Pro')
  })

  it('should set default document title on unmount', () => {
    // given
    const { unmount } = render(<PageTitle title="My title" />)

    // when
    unmount()

    // then
    expect(document.title).toBe('pass Culture Pro')
  })
})
