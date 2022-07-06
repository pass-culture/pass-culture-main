import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'

import CopyLink from 'ui-kit/CopyLink'
import { ICopyLink } from 'ui-kit/CopyLink/CopyLink'
import React from 'react'
import userEvent from '@testing-library/user-event'

const renderCopyLink = (props: ICopyLink) => {
  return render(<CopyLink {...props} />)
}

describe('Copy link button', () => {
  it('should display component with enabled button', async () => {
    // Given
    const props = {
      textToCopy: 'mYc0dE',
    }

    // When
    renderCopyLink(props)
    const code = screen.getByText('mYc0dE')
    const button = screen.getByText('Copier')

    // Then
    expect(code).toBeInTheDocument()
    expect(button).toBeInTheDocument()
  })

  it('should copy props onclick', async () => {
    // Given
    const props = {
      textToCopy: 'mYc0dE',
    }
    renderCopyLink(props)
    const copyCommand = (document.execCommand = jest.fn())

    // When
    const button = screen.getByText('Copier')
    await userEvent.click(button)

    // Then
    expect(copyCommand).toHaveBeenCalledWith('copy', true, 'mYc0dE')
  })
})
