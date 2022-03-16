import { render, screen } from '@testing-library/react'
import React from 'react'
import '@testing-library/jest-dom'

import BannerRGS from '../BannerRGS'

describe('src | new_components | BannerRGS', () => {
  it('should render a link to RGS information', () => {
    render(<BannerRGS />)
    expect(
      screen.getByRole('link', {
        name: 'Consulter nos recommendations de sécurité',
      })
    ).toHaveAttribute(
      'href',
      'https://aide.passculture.app/hc/fr/articles/4458607720732--Acteurs-Culturels-Comment-assurer-la-s%C3%A9curit%C3%A9-de-votre-compte-'
    )
  })
})
