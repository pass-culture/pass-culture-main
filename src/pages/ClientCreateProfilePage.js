import React, { Component } from 'react'

class ClientCreateProfilePage extends Component {
  constructor () {
    super()
    this.state = { 'question_index' : 0 };
  }
  
  questions = [
                [{title: 'Booba',  img: 'booba.jpg' }, {title: 'Orelsan',  img: 'orelsan.jpg' }],
                [{title: 'Booba2', img: 'booba2.jpg'}, {title: 'Orelsan2', img: 'orelsan2.jpg'}],
                [{title: 'Booba3', img: 'booba3.jpg'}, {title: 'Orelsan3', img: 'orelsan3.jpg'}]
              ]
  
  handleChoice = (event) => {
    console.log("clicked");
    this.setState(prevState => { console.log(prevState); return { question_index: prevState.question_index+1 } });
  }

  renderChoice = (question_index, choice_index) => {
    let question = this.questions[question_index];
    return (
        <div className='choice' data-choice='{number}' onClick={this.handleChoice}>
          <div className='choice-title'>{question[choice_index].title}</div>
          <img className='choice-img' alt='' src={question[choice_index].img} />
        </div>
      )
  }
  
  render = () => {
    return (
      <main className='page client-create-profile-page flex flex-column'>
        <h2>Aidez Pass Culture à vous connaître</h2>
        <h3>Vous êtes plutôt</h3>
        { this.renderChoice(this.state.question_index, 0) }
        <div className='or'>OU</div>
        { this.renderChoice(this.state.question_index, 1) }
      </main>
    )
  }
}

export default ClientCreateProfilePage
