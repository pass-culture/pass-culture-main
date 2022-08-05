import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import BannerRGS from '../BannerRGS'

describe('src | new_components | BannerRGS', () => {
  it('should render a link to RGS information', () => {
    render(<BannerRGS />)
    expect(
      screen.getByRole('link', {
        name: 'Consulter nos recommandations de sécurité',
      })
    ).toHaveAttribute(
      'href',
      'https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte-'
    )
  })
  it('should close the banner', async () => {
    const spyClose = jest.fn()
    render(<BannerRGS closable onClose={spyClose} />)
    await userEvent.click(
      screen.getByRole('button', {
        name: 'Masquer le bandeau',
      })
    )
    expect(spyClose).toHaveBeenCalledTimes(1)
  })
})
