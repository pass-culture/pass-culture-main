import { render, screen } from '@testing-library/react'
import React from 'react'

import { FormLayoutDescription } from '..'
import { FormLayoutDescriptionProps } from '../FormLayoutDescription'

const renderFormLayoutDescription = ({
  description,
  isBanner,
  links,
}: FormLayoutDescriptionProps) => {
  render(
    <FormLayoutDescription
      description={description}
      links={links}
      isBanner={isBanner}
    />
  )
}

describe('Description', () => {
  let descriptionProps: FormLayoutDescriptionProps

  beforeEach(() => {
    descriptionProps = {
      description: 'This is a description',
    }
  })

  it('should render the description as text', async () => {
    renderFormLayoutDescription(descriptionProps)
    expect(screen.getByText('This is a description')).toBeInTheDocument()
  })

  it('should render the description as a banner', async () => {
    descriptionProps.isBanner = true
    renderFormLayoutDescription(descriptionProps)
    expect(screen.getByText('This is a description')).toBeInTheDocument()
  })

  it('should not render component', async () => {
    descriptionProps.description = undefined
    renderFormLayoutDescription(descriptionProps)
    expect(screen.queryByText('This is a description')).not.toBeInTheDocument()
  })
})
