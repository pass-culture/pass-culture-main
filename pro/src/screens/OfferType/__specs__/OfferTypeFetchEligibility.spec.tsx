import { render, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import { getOfferTypePageElements } from '../__tests-utils__/offerTypeUtils'
import { setDefaultProps } from '../__tests-utils__/setDefaultProps'
import OfferType, { IOfferTypeProps } from '../OfferType'

const renderEACOfferCreation = (props: IOfferTypeProps) => {
  const history = createBrowserHistory()
  return render(
    <Router history={history}>
      <OfferType {...props} />
    </Router>
  )
}

describe('screens | OfferType', () => {
  let props: IOfferTypeProps

  beforeEach(() => {
    props = setDefaultProps()
  })

  it('should prevent submitting if offerer is not eligible to eac', async () => {
    const testProps = {
      ...props,
      fetchCanOffererCreateEducationalOffer: jest.fn().mockRejectedValue({}),
    }
    renderEACOfferCreation(testProps)

    const { educationalOfferButton, submitButton } = getOfferTypePageElements()
    userEvent.click(educationalOfferButton)

    await waitFor(() => {
      expect(
        testProps.fetchCanOffererCreateEducationalOffer
      ).toHaveBeenCalledWith()
    })

    expect(educationalOfferButton).toHaveProperty('disabled')
    expect(submitButton).toHaveProperty('disabled')
  })
})
