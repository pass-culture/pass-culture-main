import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'

import { BannerSummary } from '../'

describe('components:BannerSummary', () => {
  it('renders component successfully when draft offers are enabled', async () => {
    render(
      <Provider store={configureTestStore()}>
        <BannerSummary />
      </Provider>
    )
    expect(
      screen.getByText(
        /Vérifiez les informations ci-dessous avant de publier votre offre./
      )
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        /Si vous souhaitez la publier plus tard, vous pouvez retrouver votre brouillon dans la liste de vos offres./
      )
    ).toBeInTheDocument()
  })
})
