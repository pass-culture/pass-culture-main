import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import { RootState } from 'store/reducers'
import { configureTestStore } from 'store/testUtils'

import AppPreviewVenue, { IAppPreviewVenueProps } from '../AppPreviewVenue'

interface IRenderAppPreviewVenueProps {
  storeOverride?: Partial<RootState>
  props: IAppPreviewVenueProps
}
const renderAppPreviewVenue = ({ props }: IRenderAppPreviewVenueProps) => {
  const store = configureTestStore()
  return render(
    <Provider store={store}>
      <AppPreviewVenue {...props} />
    </Provider>
  )
}

describe('AppPreviewVenue', () => {
  let props: IAppPreviewVenueProps

  beforeEach(() => {
    props = {
      imageUrl: '/noimage.jpg',
    }
  })

  it('should render app preview venue', async () => {
    await renderAppPreviewVenue({
      props,
    })
    expect(screen.getByTestId('app-preview-venue-img-home')).toBeInTheDocument()
    expect(screen.getByTestId('app-preview-venue-img')).toBeInTheDocument()
  })
})
