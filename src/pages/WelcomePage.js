import React from 'react'

const WelcomePage = ({}) => {
  return (
    <main className='page flex items-center justify-center'>
      <div className='center'>
        <div className='h1 mb3'>
          Bienvenue sur le pass
        </div>
        <div className='h3 mb3'>
          Prépare-toi pour un rapide quizz pour savoir tes goûts
        </div>
        <button className='button button--alive'>
          Ok let's go
        </button>
      </div>
    </main>
  )
}

export default WelcomePage
