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
    <b>{label || ''}</b>
  </span>
)

export default renderLabel
