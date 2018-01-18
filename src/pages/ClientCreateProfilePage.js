import React, { Component } from 'react'
import { withRouter } from 'react-router'

class ClientCreateProfilePage extends Component {
  constructor () {
    super()
    this.state = { 'question_index' : 0 };
  }

  questions = [
                ['concert','casque'],
                ['bouquin','bd'],
                ['sculpture','peinture'],
                ['theatre','standup'],
                ['naruto','goku'],
                ['jeuxdetable','vj']
              ]

  handleChoice = (event) => {
    if (this.state.question_index === this.questions.length-1) {
      this.props.history.push('/offres/');
      return;
    }
    this.setState(prevState => { console.log(prevState); return { question_index: prevState.question_index+1 } });
  }

  renderChoice = (question_index, choice_index) => {
    let question = this.questions[question_index];
    return (
        <div className='choice' data-index={choice_index} onClick={this.handleChoice}>
          <img className='choice-img' alt={question[choice_index]} src={'/images_questions/'+question[choice_index]+'_300.jpg'} srcSet={'/images_questions/'+question[choice_index]+'_600.jpg 600w'} />
        </div>
      )
  }

  render = () => {
    return (
      <main className='page client-create-profile-page flex flex-column'>
        <h2>Aidez Pass Culture à vous connaître</h2>
        <h3>Vous êtes plutôt&nbsp;:</h3>
        <div className='choices'>
          { this.renderChoice(this.state.question_index, 0) }
          <div className='or'>OU</div>
          { this.renderChoice(this.state.question_index, 1) }
        </div>
      </main>
    )
  }
}

export default withRouter(ClientCreateProfilePage)
