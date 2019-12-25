import React from 'react';
// import axios from 'axios';

class SearchForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: '',
      typing: false,
      // suggest: '',
      typingTimeout: 0
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
  }

  handleChange(event) {
    this.setState({value: event.target.value});
    if(this.state.typingTimeout){
      clearTimeout(this.state.typingTimeout)
    }
    this.setState({
      value: event.target.value,
      typing: false,
      typingTimeout: setTimeout(() => {
        this.props.callback(this.state.value, false)
      }, 300)
    })
    // if(event.target.value.length > 2){
    //   axios.post('/suggest/'+event.target.value)
    //   .then( response => {
    //     if(response.data.length > 0)
    //       this.setState({suggest: response.data[0].suggest.toLowerCase()})
    //   }).catch(error => console.error(error))
    // } else{
    //   this.setState({suggest: ''})
    // }
  }

  handleSubmit(event) {
    if(this.state.value.length > 0)
        this.props.callback(this.state.value, true)
    event.preventDefault();
  }

  handleKeyDown(event){
    // if(event.keyCode === 9 && this.state.value.length < this.state.suggest.length){
    //   this.props.callback('"'+this.state.suggest+'"', false)
    //   this.setState({value: this.state.suggest})
    //   event.preventDefault()
    // }
    if(event.key === 'Enter'){
      event.preventDefault()
      this.handleSubmit(event)
    }
  }

  render() {
    return (
      <form className="search-form" onSubmit={this.handleSubmit}>
          <div className="editable item">
            <input className="search-input search-suggestion"
              type="text"
              placeholder={this.state.value.length > 2 ? this.state.suggest : ''}
              disabled="True"
            />
            <input className="search-input search-main"
              id="search-input-box"
              placeholder="Search Books"
              type="text" 
              value={this.state.value}
              onChange={this.handleChange}
              onKeyDown={this.handleKeyDown}
            />
            </div>
          <div className="item" style={{paddingTop: '5px', color: 'gray', fontSize: '14px'}} >Hit Enter to load all results.&nbsp;
          <a href="https://sqlite.org/fts5.html#full_text_query_syntax" target="_blank" rel="noopener noreferrer">
            Query Syntax
          </a>
          </div>
      </form>
    );
  }
}

export default SearchForm;