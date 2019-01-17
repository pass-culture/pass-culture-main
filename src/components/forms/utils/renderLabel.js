/* eslint
  react/jsx-one-expression-per-line: 0 */
//
//
// NOTE ---------------------- DEPRECATED ----------------------
//
//
import React from 'react'

export const renderLabel = (label = '') => (
  <span>
    <span>{label || ''}</span>
  </span>
)

export default renderLabel
