import React from 'react'

import Tooltip from 'ui-kit/Tooltip'

import { getLabelString } from '../getLabelString'

describe('getLabelString', () => {
  it('should return label as string', async () => {
    expect(getLabelString('Input Label')).toBe('Input Label')
  })
  it('should return empty string if label is a component', async () => {
    expect(
      getLabelString(
        <Tooltip id={'tooltip-id'} content={'Label'}>
          Button
        </Tooltip>
      )
    ).toBe('')
  })
})
