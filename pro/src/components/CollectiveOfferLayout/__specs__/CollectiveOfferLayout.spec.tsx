import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import CollectiveOfferLayout from '../CollectiveOfferLayout'

const renderCollectiveOfferLayout = ({
  isTemplate,
  title,
  subTitle,
}: {
  isTemplate?: boolean
  title: string
  subTitle?: string
}) => {
  render(
    <CollectiveOfferLayout
      title={title}
      subTitle={subTitle}
      isTemplate={isTemplate}
    >
      Test
    </CollectiveOfferLayout>
  )
}

describe('CollectiveOfferLayout', () => {
  let props: { isTemplate?: boolean; title: string; subTitle?: string }
  beforeEach(() => {
    props = {
      title: 'Offre collective',
      subTitle: 'Ma super offre',
    }
  })
  it('should render subtitle if provided', () => {
    renderCollectiveOfferLayout(props)

    const offerTitle = screen.getByText('Offre collective')
    const offersubTitle = screen.getByText('Ma super offre')
    const tagOfferTemplate = screen.queryByText('Offre vitrine')

    expect(offerTitle).toBeInTheDocument()
    expect(offersubTitle).toBeInTheDocument()
    expect(tagOfferTemplate).not.toBeInTheDocument()
  })
  it("should render 'offer template' tag is offer is template", () => {
    props.isTemplate = true
    renderCollectiveOfferLayout(props)

    const tagOfferTemplate = screen.getByText('Offre vitrine')

    expect(tagOfferTemplate).toBeInTheDocument()
  })
})
