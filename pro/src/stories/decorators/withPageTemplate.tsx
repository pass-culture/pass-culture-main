import React from 'react'

type GetStory = () => React.ReactNode;

export const withPageTemplate = (getStory: GetStory): React.ReactNode => {
  return (
    <>
      <div />
      <main className='container'>
        <div className='page-content'>
          <div className='after-notification-content'>
            {getStory()}
          </div>
        </div>
      </main>
      <div />
    </>
  )
}
