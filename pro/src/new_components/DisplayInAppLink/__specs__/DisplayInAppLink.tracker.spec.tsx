import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import { DisplayInAppLink, IDisplayInAppLinkProps } from '..'
import { configureTestStore } from '../../../store/testUtils'

window.open = jest.fn()
const mockLogEvent = jest.fn()

const renderDisplayInAppLink = async (props: IDisplayInAppLinkProps) => {
  const store = configureTestStore()

  return render(
    <Provider store={store}>
      <DisplayInAppLink {...props}>
        <p>clique moi</p>
      </DisplayInAppLink>
    </Provider>
  )
}
describe('tracker DisplayInAppLink', () => {
  it('should track offer when clicking on link', async () => {
    const props = {
      link: 'example.com',
      tracking: { isTracked: true, trackingFunction: mockLogEvent },
    }

    renderDisplayInAppLink(props)

    await userEvent.click(screen.getByText('clique moi'))
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
  })
})
