/* istanbul ignore file */
import '@testing-library/jest-dom'

import { render } from '@testing-library/react'
import React from 'react'
import { MemoryRouter } from 'react-router-dom'

import ThumbnailDialog from 'pages/Offers/Offer/Thumbnail/ThumbnailDialog'

jest.mock('repository/pcapi/pcapi', () => ({
  ...jest.requireActual('repository/pcapi/pcapi'),
}))

export const renderThumbnail = ({
  setIsModalOpened = jest.fn(),
  setThumbnailInfo = jest.fn(),
  postThumbnail = jest.fn(),
} = {}) => {
  render(
    <MemoryRouter>
      <ThumbnailDialog
        postThumbnail={postThumbnail}
        setIsModalOpened={setIsModalOpened}
        setPreview={jest.fn()}
        setThumbnailInfo={setThumbnailInfo}
      />
    </MemoryRouter>
  )
}
