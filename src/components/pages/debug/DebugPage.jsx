import React from 'react'

function generateError() {
  throw new Error('Generated error from Debug page')
}

const Debug = () => (
  <main className="debug-main">
    <button
      className="db-create-error"
      onClick={generateError}
      type="button"
    >
      {'Générer une erreur'}
    </button>
  </main>
)

export default Debug
