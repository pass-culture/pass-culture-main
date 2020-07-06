import React from 'react'
import { generateError } from './domain/generateError'

const Debug = () => (
  <main className="debug-main">
    <div className="debug-actions-wrapper">
      <button
        className="db-generate-error"
        onClick={generateError}
        type="button"
      >
        {'Générer une erreur'}
      </button>
    </div>
  </main>
)

export default Debug
