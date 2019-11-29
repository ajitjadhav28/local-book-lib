import React from 'react';
import searchLogo from './search.png'

function SeachFavicon(props){
  props = props.props
  return(
    <img style={{'width': props.width, 'height': props.height, 'verticalAlign': 'top'}} src={searchLogo}></img>
  )
}

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
          {/* <SeachFavicon props={{'height':35, 'width':35}} /> */}
          <input className="search-input" placeholder="   Search Books" type="text" value={this.state.value} onChange={this.handleChange} />
      </form>
    );
  }
}

export default SearchForm;