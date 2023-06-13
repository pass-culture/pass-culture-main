import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'

import * as apiHelpers from 'apiClient/helpers'
import { UploaderModeEnum } from 'components/ImageUploader/types'
import { renderWithProviders } from 'utils/renderWithProviders'

import ButtonImageEdit, { ButtonImageEditProps } from '../ButtonImageEdit'

const renderButtonImageEdit = (props: ButtonImageEditProps) =>
  renderWithProviders(<ButtonImageEdit {...props} />)

describe('test ButtonImageEdit', () => {
  let props: ButtonImageEditProps
  beforeEach(() => {
    props = {
      mode: UploaderModeEnum.OFFER,
      onImageUpload: jest.fn(),
    }
  })

  it('should render add button', async () => {
    renderButtonImageEdit(props)
    expect(
      await screen.findByRole('button', {
        name: /Ajouter une image/,
      })
    ).toBeInTheDocument()
  })

  it('should render edit button', async () => {
    props = {
      ...props,
      initialValues: {
        ...props.initialValues,
        imageUrl: 'http://test.url',
      },
    }
    renderButtonImageEdit(props)
    expect(
      await screen.findByRole('button', {
        name: /Modifier/,
      })
    ).toBeInTheDocument()
  })

  it('should open modal on click on add image button', async () => {
    renderButtonImageEdit(props)
    await userEvent.click(
      await screen.findByRole('button', {
        name: /Ajouter une image/,
      })
    )
    expect(
      await screen.findByRole('heading', {
        name: /Ajouter une image/,
      })
    ).toBeInTheDocument()
  })

  it('should render edit button', async () => {
    props = {
      ...props,
      initialValues: {
        imageUrl: 'http://test.url',
        originalImageUrl: 'http://test.url',
        credit: 'John Do',
      },
    }
    jest
      .spyOn(apiHelpers, 'getFileFromURL')
      .mockResolvedValue(new File([''], 'myThumb.png'))
    renderButtonImageEdit(props)
    await userEvent.click(
      await screen.findByRole('button', {
        name: /Modifier/,
      })
    )
    expect(
      await screen.findByRole('heading', {
        name: /Ajouter une image/,
      })
    ).toBeInTheDocument()
  })
})
