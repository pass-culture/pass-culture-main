import { fireEvent, render, waitFor } from '@testing-library/react'
import { createBrowserHistory } from 'history'
import React from 'react'
import { Router } from 'react-router'

import '@testing-library/jest-dom'
import {
  getEligibilityBanner,
  getOffererSelect,
} from '../__tests-utils__/eacOfferCreationUtils'
import setDefaultProps from '../__tests-utils__/setDefaultProps'
import { userOfferersFactory } from '../__tests-utils__/userOfferersFactory'
import OfferEducational, { IOfferEducationalProps } from '../OfferEducational'

const renderEACOfferCreation = (
  props: IOfferEducationalProps,
  overrideProps?: Partial<IOfferEducationalProps>
) => {
  const history = createBrowserHistory()
  return render(
    <Router history={history}>
      <OfferEducational {...props} {...overrideProps} />
    </Router>
  )
}

describe('screens | OfferEducational | FetchEligibility', () => {
  let props: IOfferEducationalProps
  beforeEach(() => {
    props = setDefaultProps()
  })
  it('should prevent submitting if offerer is not eligible to eac', async () => {
    const testProps = {
      ...props,
      getIsOffererEligibleToEducationalOfferAdapter: jest
        .fn()
        .mockResolvedValue({
          isOk: true,
          message: null,
          payload: {
            isOffererEligibleToEducationalOffer: false,
          },
        }),
      userOfferers: userOfferersFactory([{ id: '1' }, { id: '2' }]),
    }
    renderEACOfferCreation(testProps)

    const offererSelect = getOffererSelect()
    fireEvent.change(offererSelect, { target: { value: '2' } })

    await waitFor(() => {
      expect(
        testProps.getIsOffererEligibleToEducationalOfferAdapter
      ).toHaveBeenCalledWith('2')
    })

    await waitFor(() => {
      const banner = getEligibilityBanner()
      expect(banner).toBeInTheDocument()
    })
  })
})
