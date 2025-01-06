import { render, screen } from '@testing-library/react'

import {
  FormLayoutDescription,
  FormLayoutDescriptionProps,
} from '../FormLayoutDescription'

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

  it('should render the description as text', () => {
    renderFormLayoutDescription(descriptionProps)
    expect(screen.getByText('This is a description')).toBeInTheDocument()
  })

  it('should render the description as a banner', () => {
    descriptionProps.isBanner = true
    renderFormLayoutDescription(descriptionProps)
    expect(screen.getByText('This is a description')).toBeInTheDocument()
  })

  it('should not render component', () => {
    descriptionProps.description = undefined
    renderFormLayoutDescription(descriptionProps)
    expect(screen.queryByText('This is a description')).not.toBeInTheDocument()
  })
})
