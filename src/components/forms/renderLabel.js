/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
// import { Icon, Tooltip } from 'antd'

const renderLabel = (label = '') => (
  <span>
    <b>{label || ''}</b>
    {/* {help && (
      <Tooltip overlayClassName="ant-tooltip-note" title={help}>
        <Icon className="ml7" type="question-circle-o" />
      </Tooltip>
    )} */}
  </span>
)

export default renderLabel
