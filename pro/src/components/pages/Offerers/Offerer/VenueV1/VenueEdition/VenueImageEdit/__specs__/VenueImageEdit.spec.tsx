import { fireEvent, render } from '@testing-library/react'
import React from 'react'

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
  onSetCredit: jest.fn(),
}

describe('venue image edit', () => {
  it('closes the modal on cancel button click', () => {
    const { getByText } = render(<VenueImageEdit {...defaultProps} />)
    fireEvent.click(getByText("Remplacer l'image"))
    expect(mockReplaceImage).toHaveBeenCalledTimes(1)
  })
})
