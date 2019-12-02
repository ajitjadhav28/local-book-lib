import React from 'react';

class SearchForm extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      value: '',
      typing: false,
      typingTimeout: 0
    };

    this.handleChange = this.handleChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
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
      }, 200)
    })
  }

  handleSubmit(event) {
    if(this.state.value.length > 0)
        this.props.callback(this.state.value, true)
    event.preventDefault();
  }

  render() {
    return (
      <form className="search-form" onSubmit={this.handleSubmit}>
          <input className="search-input" placeholder="   Search Books" type="text" value={this.state.value} onChange={this.handleChange} />
          <div style={{paddingTop: '3px', color: 'gray'}} >Hit Enter to load all results.&nbsp;
          <a href="https://sqlite.org/fts5.html#full_text_query_syntax" target="_blank">
            Query Syntax
          </a>
          </div>
      </form>
    );
  }
}

export default SearchForm;