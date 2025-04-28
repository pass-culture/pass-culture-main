import { render, screen } from '@testing-library/react'

import { RootState } from 'commons/store/rootReducer'

import { AppPreviewOffer, AppPreviewOfferProps } from './AppPreviewOffer'

interface RenderAppPreviewOfferProps {
  storeOverride?: Partial<RootState>
  props: AppPreviewOfferProps
}
const renderAppPreviewOffer = ({ props }: RenderAppPreviewOfferProps) => {
  return render(<AppPreviewOffer {...props} />)
}

describe('AppPreviewOffer', () => {
  let props: AppPreviewOfferProps

  beforeEach(() => {
    props = {
      imageUrl: '/noimage.jpg',
    }
  })

  it('should render app preview offer', () => {
    renderAppPreviewOffer({ props })

    expect(screen.getByTestId('app-preview-offer-img-home')).toBeInTheDocument()
    expect(screen.getByTestId('app-preview-offer-img')).toBeInTheDocument()
  })
})
