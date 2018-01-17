import React, { Component } from 'react'
import { withRouter } from 'react-router'

class ClientCreateProfilePage extends Component {
  constructor () {
    super()
    this.state = { 'question_index' : 0 };
  }
  
  questions = [
                [{title: 'Booba',  img: 'booba' }, {title: 'Orelsan',  img: 'orelsan' }],
                [{title: 'Booba2', img: 'booba2'}, {title: 'Orelsan2', img: 'orelsan2'}],
                [{title: 'Booba3', img: 'booba'}, {title: 'Orelsan3', img: 'orelsan'}]
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
          <img className='choice-img' alt={question[choice_index].title} src={'/images_questions/'+question[choice_index].img+'_300.jpg'} />
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
