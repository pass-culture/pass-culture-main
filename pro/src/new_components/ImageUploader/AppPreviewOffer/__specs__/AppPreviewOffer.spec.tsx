import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import { RootState } from 'store/reducers'

import AppPreviewOffer, { IAppPreviewOfferProps } from '../AppPreviewOffer'

interface IRenderAppPreviewOfferProps {
  storeOverride?: Partial<RootState>
  props: IAppPreviewOfferProps
}
const renderAppPreviewOffer = ({ props }: IRenderAppPreviewOfferProps) => {
  return render(<AppPreviewOffer {...props} />)
}

describe('AppPreviewOffer', () => {
  let props: IAppPreviewOfferProps

  beforeEach(() => {
    props = {
      imageUrl: '/noimage.jpg',
    }
  })

  it('should render app preview offer', async () => {
    await renderAppPreviewOffer({
      props,
    })
    expect(screen.getByTestId('app-preview-offer-img-home')).toBeInTheDocument()
    expect(screen.getByTestId('app-preview-offer-img')).toBeInTheDocument()
  })
})
