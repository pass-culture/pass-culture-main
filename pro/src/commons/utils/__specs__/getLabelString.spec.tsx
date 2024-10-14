import React from 'react'

import { Tooltip } from 'ui-kit/Tooltip/Tooltip'

import { getLabelString } from '../getLabelString'

describe('getLabelString', () => {
  it('should return label as string', () => {
    expect(getLabelString('Input Label')).toBe('Input Label')
  })

  it('should return empty string if label is a component', () => {
    expect(
      getLabelString(
        <Tooltip visuallyHidden={false} content={'Label'}>
          Button
        </Tooltip>
      )
    ).toBe('')
  })
})
