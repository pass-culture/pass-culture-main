import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import { Provider } from 'react-redux'

import * as useAnalytics from 'components/hooks/useAnalytics'
import { Events } from 'core/FirebaseEvents/constants'

import { DisplayInAppLink, IDisplayInAppLinkProps } from '..'
import { configureTestStore } from '../../../store/testUtils'

const mockLogEvent = jest.fn()

window.open = jest.fn()

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
    jest.spyOn(useAnalytics, 'default').mockImplementation(() => ({
      logEvent: mockLogEvent,
      setLogEvent: null,
    }))

    const props = {
      link: 'example.com',
      trackOffer: true,
    }

    renderDisplayInAppLink(props)

    await userEvent.click(screen.getByText('clique moi'))
    expect(mockLogEvent).toHaveBeenCalledTimes(1)
    expect(mockLogEvent).toHaveBeenNthCalledWith(
      1,
      Events.CLICKED_OFFER_FORM_NAVIGATION,
      {
        from: 'confirmation',
        isEdition: false,
        to: 'AppPreview',
        used: 'ConfirmationPreview',
      }
    )
  })
})
