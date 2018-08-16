import React from 'react'
import { Icon, Tooltip } from 'antd'

const renderLabel = (label = '', help = null) =>
  (help && (
    <span className="label">
      <b>
        {label || ''}
      </b>
      <Tooltip overlayClassName="ant-tooltip-note" title={help}>
        <Icon className="ml7" type="question-circle-o" />
      </Tooltip>
    </span>
  )) ||
  label

export default renderLabel
