import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import { renderWithProviders } from 'utils/renderWithProviders'

import { ButtonLinkNewWindow, IButtonLinkNewWindowProps } from '..'

window.open = jest.fn()
const mockLogEvent = jest.fn()

const renderButtonLinkNewWindow = (props: IButtonLinkNewWindowProps) =>
  renderWithProviders(
    <ButtonLinkNewWindow {...props}>
      <p>clique moi</p>
    </ButtonLinkNewWindow>
  )

describe('tracker ButtonLinkNewWindow', () => {
  it('should track offer when clicking on link', async () => {
    const props = {
      linkTo: 'example.com',
      tracking: { isTracked: true, trackingFunction: mockLogEvent },
    }

    renderButtonLinkNewWindow(props)

    await userEvent.click(screen.getByText('clique moi'))
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
  })
})
