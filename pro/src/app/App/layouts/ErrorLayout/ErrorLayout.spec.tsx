import { screen } from '@testing-library/react'

import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { ErrorLayout } from './ErrorLayout'

const renderErrorLayout = () => {
  return renderWithProviders(
    <ErrorLayout
      mainHeading="Error"
      paragraph="A paragraph that explains the error"
      errorIcon="ErrorIcon"
    />
  )
}

describe('ErrorLayout', () => {
  it('should always render a main landmark and a heading level 1', () => {
    renderErrorLayout()

    expect(screen.getByRole('main')).toBeInTheDocument()
    expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument()
  })
})
