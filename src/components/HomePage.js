import React from 'react'
import SearchForm from './SearchForm'
import axios from 'axios'
import BookCard from './Card'

class HomePage extends React.Component
{
    constructor(props){
        super(props)
        this.state = {
            books: false,
            initialBooks: false,
            search: ''
        }
        this.handleSearchCallback = this.handleSearchCallback.bind(this)
    }

    componentDidMount(){
        let search = "/programming OR operating system OR algorithm OR Data Structures OR science/30"
        axios.post(search).then(
            (response) => {
                this.setState({
                    books: response.data,
                    initialBooks: response.data
                })
            }
        )
    }

    handleSearchCallback(search_text, submit){
        if(search_text.length > 0){
        if(submit){
            axios.post("/"+search_text).then(
                (response) => {
                    this.setState({
                        books: response.data ? response.data : []
                    })
                }
            )
        }else if(search_text.length > this.state.search.length) {
          axios.post("/"+search_text+"/"+ 6).then(
            (response) => {
                this.setState({
                    books: response.data ? response.data : []
                })
            }
          )
        }
        this.setState({search: search_text})
        }
        else{
            this.setState({
                books: this.state.initialBooks,
                search: ''
            })
        }
        
    }

    render(){
        if(this.state.books){
        return(
            <React.Fragment>
                <div className="search-wraper">
                    <SearchForm callback={this.handleSearchCallback}/>
                </div>
                <div className="book-wraper" >
                    {
                        this.state.books.map(book =>
                            <BookCard
                                key={book.isbn == true ? book.isbn : book.url.substring(27, book.url.length)}
                                props={{...book}}
                            />
                        )
                    }
                </div>
            </React.Fragment>
        )
    }
    else return ""
    }
}

export default HomePage;