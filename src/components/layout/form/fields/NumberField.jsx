import React from 'react'

import TextField from './TextField'

export const NumberField = props =>
  <TextField {...props}
             type="number"
             pattern="[0-9]+([\.,][0-9]+)?"
             step="0.01"
  />
