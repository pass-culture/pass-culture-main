import { fireEvent, render } from '@testing-library/react'
import React from 'react'
import { Provider } from 'react-redux'

import { configureTestStore } from 'store/testUtils'

import { VenueImageEdit } from '../VenueImageEdit'

const mockReplaceImage = jest.fn()
const defaultProps = {
  image: new File([], 'toto.png', {
    type: 'image/png',
  }),
  onSetImage: jest.fn(),
  onReplaceImage: mockReplaceImage,
  credit: '',
  onEditedImageSave: jest.fn(),
  saveInitialPosition: jest.fn(),
  saveInitialScale: jest.fn(),
  onSetCredit: jest.fn(),
}

describe('venue image edit', () => {
  it('closes the modal on cancel button click', () => {
    const storeOverrides = {
      features: {
        list: [
          {
            isActive: false,
            nameKey: 'PRO_ENABLE_UPLOAD_VENUE_IMAGE',
          },
        ],
      },
    }
    const store = configureTestStore(storeOverrides)
    const { getByText } = render(
      <Provider store={store}>
        <VenueImageEdit {...defaultProps} />
      </Provider>
    )
    fireEvent.click(getByText("Remplacer l'image"))
    expect(mockReplaceImage).toHaveBeenCalledTimes(1)
  })
})
