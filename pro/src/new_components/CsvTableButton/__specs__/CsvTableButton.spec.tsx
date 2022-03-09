import '@testing-library/jest-dom'

import { fireEvent, render, screen } from '@testing-library/react'
import React from 'react'

import type { CsvTableButtonProps } from '../'
import { CsvTableButton } from '../'

describe('src | components | layout | CsvTableButton', () => {
  let props: CsvTableButtonProps

  beforeEach(() => {
    props = {
      children: 'foobar',
      history: {
        push: jest.fn(),
      },
      href: '/path-to-csv',
      location: {
        pathname: '/fake-url',
      },
    } as unknown as CsvTableButtonProps
  })

  describe('render', () => {
    it('should render a button with the default props', () => {
      // when
      render(<CsvTableButton {...props} />)

      // then
      const children = screen.getByText('foobar')
      expect(children).toBeInTheDocument()
    })
  })

  describe('redirection', () => {
    it('should redirect to next url when clicking on button', () => {
      // given
      render(<CsvTableButton {...props} />)

      // when
      const button = screen.getByRole('button')
      fireEvent.click(button)

      // then
      expect(props.history.push).toHaveBeenCalledWith(
        '/fake-url/detail',
        '/path-to-csv'
      )
    })
  })
})
