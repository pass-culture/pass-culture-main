import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import React from 'react'

import { ApiKeyType } from '../../Offerer'
import ApiKey from '../ApiKey'

describe('src | Offerer | ApiKey', () => {
  const props = new ApiKeyType({
    maxAllowed: 5,
    prefixes: ['key-prefix1'],
  })
  it('should display api keys', () => {
    render(<ApiKey apiKey={props} />)

    expect(screen.getByText('key-prefix1********')).toBeInTheDocument()
    expect(screen.getByText('1/5').closest('div')).toHaveAttribute(
      'class',
      'api-key-title__counter'
    )
  })
  it('should display red color if limit reached', () => {
    props.prefixes = ['key1', 'key2', 'key3', 'key4', 'key5']

    // when
    render(<ApiKey apiKey={props} />)

    // then
    expect(screen.getByText('5/5').closest('div')).toHaveAttribute(
      'class',
      'api-key-title__counter api-key-title__counter--error'
    )
  })
})
