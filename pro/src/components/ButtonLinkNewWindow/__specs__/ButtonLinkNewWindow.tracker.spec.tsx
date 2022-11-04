import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import { ButtonLinkNewWindow, IButtonLinkNewWindowProps } from '..'
import { configureTestStore } from '../../../store/testUtils'

window.open = jest.fn()
const mockLogEvent = jest.fn()

const renderButtonLinkNewWindow = async (props: IButtonLinkNewWindowProps) => {
  const store = configureTestStore()

  return render(
    <Provider store={store}>
      <ButtonLinkNewWindow {...props}>
        <p>clique moi</p>
      </ButtonLinkNewWindow>
    </Provider>
  )
}
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
