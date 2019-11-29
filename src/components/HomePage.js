import React from 'react'
import SearchForm from './SearchForm'
import { randomBytes } from 'crypto';
import axios from 'axios'
import BookCard from './Card'

let ProxyServer = "http://127.0.0.28:9999"

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
        axios.post(ProxyServer+search).then(
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
          this.setState({search: search_text})
        if(submit){
            axios.post(ProxyServer+"/"+search_text).then(
                (response) => {
                    this.setState({
                        books: response.data ? response.data : []
                    })
                }
            )
        }else {
          axios.post(ProxyServer+"/"+search_text+"/"+ 6).then(
            (response) => {
                this.setState({
                    books: response.data ? response.data : []
                })
            }
          )
        }}
        else{
            this.setState({
                books: this.state.initialBooks
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
                            <BookCard key={ randomBytes(10) } props={{...book}} />
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