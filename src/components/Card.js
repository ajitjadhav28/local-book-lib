import React from 'react'

function CardDownload(props){
    let data = props.props
    if(data.pdf_url != "None" && data.epub_url != "None"){
      return (
        <React.Fragment>
          <a className="book-link-pdf App-link" href={data.pdf_url}>PDF({(data.pdf_size/(1024*1024)).toFixed(2)}MB)</a>
          <a className="book-link-epub App-link" href={data.epub_url}>EPUB({(data.epub_size/(1024*1024)).toFixed(2)}MB)</a>
        </React.Fragment>
      )
    }
    if (data.pdf_url) {
      return (<a className="book-link-pdf App-link" href={props.props.pdf_url}>PDF({(data.pdf_size/(1024*1024)).toFixed(2)}MB)</a>)
    }
    if (data.epub_url) {
      return (<a className="book-link-epub App-link" href={props.props.epub_url}>EPUB({(data.epub_size/(1024*1024)).toFixed(2)}MB)</a>)
    }
  }
  
  function BookCard(props){
    return(
      <div className="book-card">
        <div className="book-card-img">
          <img className="book-card-img-tag" src={"data:image/jpeg;base64,".concat(props.props.image)}></img>
        </div>
        <div className="book-card-details">
          <div className="book-card-tite">
            <span className="card-span-title"> {props.props.title} </span>
          </div>
          <div className="book-card-subtitle">
            {props.sub_title}
          </div>
          <div className="book-card-description">
            <p>{props.props.description.substring(0, 300) }</p>
          </div>
          <div className="book-card-details">
              <span style={{'margin-left': '10px'}}> Author: {props.props.author} </span>
              <span style={{'margin-left': '10px'}}> Published: {props.props.year} </span>
              <span style={{'margin-left': '10px'}}> Pages: {props.props.pages} </span>
          </div>
          <div className="book-card-download">
            <CardDownload props={props.props} />
          </div>
        </div>
      </div>
    )
  }

export default BookCard