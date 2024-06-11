import { screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import React from 'react'

import { CalloutVariant } from 'components/Callout/types'
import { renderWithProviders } from 'utils/renderWithProviders'

import { Callout, CalloutProps } from '../Callout'

describe('Callout', () => {
  const props: CalloutProps = {
    title: 'This is a banner warning',
    links: [
      {
        href: '/some/site',
        label: 'link label',
        icon: null,
        isExternal: true,
      },
    ],
  }

  it('should display title, content and links', () => {
    renderWithProviders(<Callout {...props}>This is the content</Callout>)

    expect(screen.getByText('This is a banner warning')).toBeInTheDocument()
    expect(screen.getByText('This is the content')).toBeInTheDocument()

    expect(
      screen.getByRole('link', {
        name: /link label/,
      })
    ).toBeInTheDocument()
    expect(screen.queryByAltText('Fermer le message')).not.toBeInTheDocument()
  })

  it('should close the Callout', async () => {
    const spyClose = vi.fn()
    renderWithProviders(
      <Callout {...{ ...props, closable: true, onClose: spyClose }} />
    )

    await userEvent.click(screen.getByLabelText('Fermer le message'))

    expect(spyClose).toHaveBeenCalledTimes(1)
  })

  it('should display an Information callout', () => {
    renderWithProviders(<Callout {...props} />)

    expect(screen.getAllByRole('img')[0]).toHaveAttribute(
      'aria-label',
      'Information'
    )
  })

  it('should display an Error callout', () => {
    renderWithProviders(<Callout {...props} variant={CalloutVariant.ERROR} />)

    expect(screen.getAllByRole('img')[0]).toHaveAttribute(
      'aria-label',
      'Erreur'
    )
  })

  it('should display a Success callout', () => {
    renderWithProviders(<Callout {...props} variant={CalloutVariant.SUCCESS} />)

    expect(screen.getAllByRole('img')[0]).toHaveAttribute(
      'aria-label',
      'Confirmation'
    )
  })

  it('should display a Warning callout', () => {
    renderWithProviders(<Callout {...props} variant={CalloutVariant.WARNING} />)

    expect(screen.getAllByRole('img')[0]).toHaveAttribute(
      'aria-label',
      'Attention'
    )
  })
})
